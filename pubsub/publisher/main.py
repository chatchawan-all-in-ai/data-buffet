#!/usr/bin/env python3
"""Data Mart -> Pub/Sub publisher (Cloud Run jobs).

Contract: document/project_wiki/cdc-process/process.md (Pub/Sub export).

  python main.py check   one task, started every 5 minutes by Cloud Scheduler: decides per export
                         table whether a new Dataform run requires a send, advances the checkpoint
                         of tables with nothing to export, and starts the send job when needed
                         (never while an execution of it is still running).
  python main.py send    N tasks in parallel, scheduling groups under the contract linked above:
                         claim -> recover from the record subscription if the previous run died ->
                         diff into a staging table -> Storage Read API -> publish batches of 1,000
                         -> record into mart_sent_state -> release.

Message envelope and per-table trigger rules are preserved from the Cloud Workflows publisher.
The current claim, recovery and deadline contracts are owned by the reference linked above.
All configuration of a table is read from process_dataset.mart_export_config BY COLUMN NAME;
send_order supplies the required group and table order.
Logs are JSON lines on stdout (Cloud Logging reads them).
"""
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

PROJECT = os.environ.get("PROJECT_ID", "databuffet-nonprd")
BQ_LOCATION = os.environ.get("BQ_LOCATION", "us-central1")
DATASET = os.environ.get("BQ_DATASET", "process_dataset")
STAGING_DATASET = os.environ.get("STAGING_DATASET", "pubsub_staging")
RECORD_TABLE = os.environ.get("RECORD_TABLE", "pubsub_record.messages")
RECORD_SUB_PREFIX = os.environ.get("RECORD_SUB_PREFIX", "rec.datamart.")
DATAFORM_REPO = os.environ.get(
    "DATAFORM_REPO", f"projects/{PROJECT}/locations/us-central1/repositories/data-buffet")
SLACK_SECRET = os.environ.get("SLACK_SECRET", "slack-datamart-dataform")
RUN_REGION = os.environ.get("RUN_REGION", "us-central1")
SEND_JOB = os.environ.get("SEND_JOB", "datamart-publish-send")
HERE = os.path.dirname(os.path.abspath(__file__))
DIFF_SQL = os.environ.get("DIFF_SQL", os.path.join(HERE, "..", "sql", "diff.sql"))

CLAIM_TIMEOUT_MINUTES = 35          # a claim older than this is expired (dead run)
FIRST_RUN_LOOKBACK_HOURS = 48       # window searched while last_invocation_end is NULL
STOP_AFTER_SECONDS = int(os.environ.get("STOP_AFTER_SECONDS", str(25 * 60)))   # graceful stop
HARD_LIMIT_SECONDS = int(os.environ.get("HARD_LIMIT_SECONDS", str(29 * 60)))   # task timeout is 30 min
BATCH_MESSAGES = 1000               # Pub/Sub limit per publish request
MAX_OUTSTANDING = 20000             # unfinished messages before publishing waits
RECORD_EVERY_ROWS = 1_000_000       # mart_sent_state is updated every this many sent rows
RECOVERY_WAIT_SECONDS = 600         # backlog of the record subscription must reach 0 within this
DATAFORM_CACHE_SECONDS = 60
CONCURRENT_ATTEMPTS = 6             # tries of a statement aborted by concurrent DML on a shared table

START = time.monotonic()


def log(severity, message, **fields):
    print(json.dumps({"severity": severity, "message": message, **fields}, default=str, ensure_ascii=False),
          flush=True)


def elapsed():
    return time.monotonic() - START


def remaining(deadline=None):
    seconds = (START + STOP_AFTER_SECONDS if deadline is None else deadline) - time.monotonic()
    if seconds <= 0:
        raise TimeoutError("task deadline reached")
    return seconds


def cleanup_deadline():
    return START + HARD_LIMIT_SECONDS


def record_deadline():
    return cleanup_deadline() - 60


def retry_concurrent(call, deadline=None):
    """Runs call(); a statement aborted by concurrent DML on a shared table is retried after a short
    random backoff, with at most CONCURRENT_ATTEMPTS attempts within the caller's deadline."""
    for attempt in range(1, CONCURRENT_ATTEMPTS + 1):
        try:
            return call()
        except Exception as e:
            text = str(e).lower()
            if attempt == CONCURRENT_ATTEMPTS or not ("concurrent update" in text or "could not serialize" in text):
                raise
            time.sleep(min(random.uniform(1, 1 + 2 * attempt), remaining(deadline)))


def now_utc():
    return datetime.now(timezone.utc)


def parse_ts(text):
    """RFC 3339 with up to nanoseconds -> aware datetime cut to microseconds (what BigQuery stores)."""
    m = re.fullmatch(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?Z", text)
    if not m:
        raise ValueError(f"unexpected timestamp {text!r}")
    micro = (m.group(2) or "0").ljust(6, "0")[:6]
    return datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S").replace(
        microsecond=int(micro), tzinfo=timezone.utc)


class Resolution:
    def __init__(self, kind, newest=None, best=None):
        self.kind = kind            # unseeded | none | advance | send
        self.newest = newest
        self.best = best


class Context:
    def __init__(self):
        from google.cloud import bigquery
        import google.auth
        from google.auth.transport.requests import AuthorizedSession
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self.bq = bigquery.Client(project=PROJECT, location=BQ_LOCATION, credentials=creds)
        self.http = AuthorizedSession(creds)
        self._listings = {}
        self._actions = {}
        self._webhook = None

    # ---- Dataform API -------------------------------------------------------------------
    def list_invocations(self, list_after):
        key = list_after.strftime("%Y-%m-%dT%H:%M:%SZ")
        cached = self._listings.get(key)
        if cached and time.monotonic() - cached[0] < DATAFORM_CACHE_SECONDS:
            return cached[1]
        params = {
            "pageSize": 1000,
            "filter": f'invocation_timing.end_time > "{key}"',
            "fields": "workflowInvocations(name,state,workflowConfig,invocationTiming/endTime),nextPageToken",
        }
        found = []
        while True:
            r = self.http.get(f"https://dataform.googleapis.com/v1beta1/{DATAFORM_REPO}/workflowInvocations",
                              params=params, timeout=min(60, remaining()))
            r.raise_for_status()
            body = r.json()
            found.extend(body.get("workflowInvocations", []))
            if not body.get("nextPageToken"):
                break
            params["pageToken"] = body["nextPageToken"]
        self._listings[key] = (time.monotonic(), found)
        return found

    def succeeded_targets(self, invocation_name):
        """Names of the actions of a Dataform invocation that SUCCEEDED (fields mask: the full
        response of a daily_process run holds every action's SQL)."""
        cached = self._actions.get(invocation_name)
        if cached is not None:
            return cached
        params = {"pageSize": 1000, "fields": "workflowInvocationActions(target/name,state),nextPageToken"}
        names = set()
        while True:
            r = self.http.get(f"https://dataform.googleapis.com/v1beta1/{invocation_name}:query",
                              params=params, timeout=min(60, remaining()))
            r.raise_for_status()
            body = r.json()
            for a in body.get("workflowInvocationActions", []):
                if a.get("state") == "SUCCEEDED":
                    names.add(a["target"]["name"])
            if not body.get("nextPageToken"):
                break
            params["pageToken"] = body["nextPageToken"]
        self._actions[invocation_name] = names
        return names

    # ---- BigQuery -----------------------------------------------------------------------
    def query(self, sql, params=None, deadline=None):
        from google.cloud import bigquery
        cfg = bigquery.QueryJobConfig(
            query_parameters=params or [], job_timeout_ms=int(remaining(deadline) * 1000))
        job = self.bq.query(sql, job_config=cfg, timeout=remaining(deadline), retry=None)
        try:
            job.result(timeout=remaining(deadline), retry=None, job_retry=None)
        except TimeoutError:
            job.cancel(timeout=min(5, remaining(cleanup_deadline())), retry=None)
            raise
        return job

    def dml(self, sql, params, deadline=None):
        return retry_concurrent(
            lambda: int(self.query(sql, params, deadline).num_dml_affected_rows or 0), deadline)

    def read_config(self):
        job = self.query(f"""
          SELECT table_name, source_view, topic, task_group, send_order,
                 last_invocation_id, last_invocation_end,
                 claimed_at, recovery_started_at, recovery_until, group_claimed_at, trigger_scheduler, seeded_at
          FROM `{PROJECT}.{DATASET}.mart_export_config`""")
        return [dict(r.items()) for r in job.result(timeout=remaining(), retry=None, job_retry=None)]

    # ---- Slack --------------------------------------------------------------------------
    def slack(self, text):
        try:
            if self._webhook is None:
                from google.cloud import secretmanager
                sm = secretmanager.SecretManagerServiceClient()
                name = f"projects/{PROJECT}/secrets/{SLACK_SECRET}/versions/latest"
                self._webhook = sm.access_secret_version(name=name, timeout=min(10, remaining(cleanup_deadline())), retry=None).payload.data.decode("utf-8").strip()
            import requests
            r = requests.post(self._webhook, json={"text": text}, timeout=min(10, remaining(cleanup_deadline())))
            r.raise_for_status()
        except Exception as e:  # the webhook URL is never logged
            log("ERROR", "Slack notification failed", error=type(e).__name__)


def claim_active(row):
    claimed = row["claimed_at"]
    return claimed is not None and claimed >= now_utc() - timedelta(minutes=CLAIM_TIMEOUT_MINUTES)


# ===== trigger rules (same as the Workflows publisher) =====================================
def resolve(ctx, row):
    if row["seeded_at"] is None:
        return Resolution("unseeded")
    last_id = row["last_invocation_id"]
    last_end = row["last_invocation_end"]
    list_after = (last_end - timedelta(seconds=1)) if last_end else now_utc() - timedelta(hours=FIRST_RUN_LOOKBACK_HOURS)
    list_after = list_after.replace(microsecond=0)
    newest = best = None
    for inv in ctx.list_invocations(list_after):
        end_text = (inv.get("invocationTiming") or {}).get("endTime")
        if end_text is None:       # still running
            continue
        inv_id = inv["name"].rsplit("/", 1)[-1]
        inv_end = parse_ts(end_text)
        if inv_id == last_id or (last_end is not None and inv_end <= last_end):
            continue
        scheduler = inv["workflowConfig"].rsplit("/", 1)[-1] if inv.get("workflowConfig") else "manual"
        candidate = {"id": inv_id, "name": inv["name"], "end": inv_end, "scheduler": scheduler}
        if newest is None or inv_end > newest["end"]:
            newest = candidate
        if inv.get("state") != "SUCCEEDED" or (best is not None and inv_end <= best["end"]):
            continue
        if row["trigger_scheduler"] is not None:
            ran = scheduler == row["trigger_scheduler"]
        else:
            ran = row["table_name"] in ctx.succeeded_targets(inv["name"])
        if ran:
            best = candidate
    if newest is None:
        return Resolution("none")
    if best is None:
        return Resolution("advance", newest=newest)
    return Resolution("send", newest=newest, best=best)


def advance_only(ctx, row, newest):
    from google.cloud import bigquery as bq
    n = ctx.dml(f"""
      UPDATE `{PROJECT}.{DATASET}.mart_export_config`
      SET last_invocation_id = @invocation_id, last_invocation_end = @invocation_end
      WHERE table_name = @table_name
        AND (claimed_at IS NULL
          OR claimed_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @m MINUTE))
        AND (last_invocation_end IS NULL OR last_invocation_end < @invocation_end)""", [
        bq.ScalarQueryParameter("table_name", "STRING", row["table_name"]),
        bq.ScalarQueryParameter("invocation_id", "STRING", newest["id"]),
        bq.ScalarQueryParameter("invocation_end", "TIMESTAMP", newest["end"]),
        bq.ScalarQueryParameter("m", "INT64", CLAIM_TIMEOUT_MINUTES)])
    log("INFO", "advanced, nothing to export", table=row["table_name"], invocation=newest["id"],
        scheduler=newest["scheduler"], rows_updated=n)


# ===== check mode ==============================================================================
def send_job_running():
    from google.cloud import run_v2
    client = run_v2.ExecutionsClient()
    parent = f"projects/{PROJECT}/locations/{RUN_REGION}/jobs/{SEND_JOB}"
    for i, execution in enumerate(client.list_executions(request={"parent": parent, "page_size": 10})):
        if not execution._pb.HasField("completion_time"):
            return execution.name
        if i >= 9:
            break
    return None


def start_send_job():
    from google.cloud import run_v2
    client = run_v2.JobsClient()
    name = f"projects/{PROJECT}/locations/{RUN_REGION}/jobs/{SEND_JOB}"
    client.run_job(request={"name": name})     # not awaited: the check job ends, the send job runs on


def check_main():
    ctx = Context()
    failed, to_send = [], []
    try:
        rows = ctx.read_config()
    except Exception as e:
        log("ERROR", "cannot read mart_export_config", error=str(e))
        ctx.slack(f":red_circle: datamart-publish failed for `mart_export_config`; {type(e).__name__}: {e}")
        return 1
    for row in rows:
        try:
            if row["seeded_at"] is None:
                continue                       # before any per-table Dataform or BigQuery call
            res = resolve(ctx, row)
            if res.kind == "advance":
                advance_only(ctx, row, res.newest)
            elif res.kind == "send" and not claim_active(row):
                to_send.append(row["table_name"])
        except Exception as e:
            log("ERROR", "check failed", table=row["table_name"], error=str(e))
            ctx.slack(f":red_circle: datamart-publish failed for `{row['table_name']}` (check job); "
                      f"last_invocation_* unchanged. Error {type(e).__name__}: {e}")
            failed.append(row["table_name"])
    if to_send:
        try:
            running = send_job_running()
            if running:
                log("INFO", "send job still running, not started again", execution=running, tables=to_send)
            else:
                start_send_job()
                log("INFO", "send job started", tables=to_send)
        except Exception as e:
            log("ERROR", "cannot start the send job", error=str(e))
            ctx.slack(f":red_circle: datamart-publish failed to start job `{SEND_JOB}`; {type(e).__name__}: {e}")
            failed.append(SEND_JOB)
    else:
        log("INFO", "nothing to send")
    return 1 if failed else 0


# ===== send mode ===============================================================================
def ordered_groups(rows):
    if not rows:
        raise ValueError("mart_export_config has no export tables")
    names = set()
    send_orders = set()
    ordered_rows = []
    for row in rows:
        name = row["table_name"]
        group = row.get("task_group")
        send_order = row.get("send_order")
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("mart_export_config requires unique, nonempty table_name values")
        if not isinstance(group, str) or not group.strip():
            raise ValueError(f"mart_export_config requires task_group for {name}")
        if not isinstance(send_order, int) or isinstance(send_order, bool):
            raise ValueError(f"mart_export_config requires send_order for {name}")
        if send_order < 1:
            raise ValueError(f"mart_export_config requires positive send_order for {name}")
        if send_order in send_orders:
            raise ValueError(f"mart_export_config requires unique send_order values; duplicate {send_order}")
        names.add(name)
        send_orders.add(send_order)
        ordered_rows.append(row)

    groups = {}
    for row in sorted(ordered_rows, key=lambda item: item["send_order"]):
        groups.setdefault(row["task_group"], []).append(row)
    return groups


def claim_group(ctx, group):
    from google.cloud import bigquery as bq
    claim = now_utc()
    n = ctx.dml(f"""
      UPDATE `{PROJECT}.{DATASET}.mart_export_config`
      SET group_claimed_at = @claim
      WHERE task_group = @group
        AND NOT EXISTS (
          SELECT 1 FROM `{PROJECT}.{DATASET}.mart_export_config`
          WHERE task_group = @group AND (
            group_claimed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @m MINUTE)
            OR claimed_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @m MINUTE)))""", [
        bq.ScalarQueryParameter("group", "STRING", group),
        bq.ScalarQueryParameter("claim", "TIMESTAMP", claim),
        bq.ScalarQueryParameter("m", "INT64", CLAIM_TIMEOUT_MINUTES)])
    return claim if n else None


def release_group(ctx, group, claim):
    from google.cloud import bigquery as bq
    ctx.dml(f"""UPDATE `{PROJECT}.{DATASET}.mart_export_config`
                SET group_claimed_at = NULL
                WHERE task_group = @group AND group_claimed_at = @claim""", [
        bq.ScalarQueryParameter("group", "STRING", group),
        bq.ScalarQueryParameter("claim", "TIMESTAMP", claim)], deadline=cleanup_deadline())


def staging_name(table_name, prefix):
    return f"{PROJECT}.{STAGING_DATASET}.{prefix}{re.sub(r'[^A-Za-z0-9_]', '_', table_name)}"


def claim_table(ctx, row, res, group_claim):
    from google.cloud import bigquery as bq
    claim = now_utc()
    n = ctx.dml(f"""
      UPDATE `{PROJECT}.{DATASET}.mart_export_config`
      SET recovery_started_at = COALESCE(recovery_started_at, claimed_at),
          recovery_until = CASE WHEN claimed_at IS NULL THEN recovery_until
            ELSE GREATEST(COALESCE(recovery_until, claimed_at),
                          TIMESTAMP_ADD(claimed_at, INTERVAL 30 MINUTE)) END,
          claimed_at = @claim
      WHERE table_name = @table_name AND group_claimed_at = @group_claim
        AND (claimed_at IS NULL
          OR claimed_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @m MINUTE))
        AND (last_invocation_end IS NULL OR last_invocation_end < @invocation_end)""", [
        bq.ScalarQueryParameter("table_name", "STRING", row["table_name"]),
        bq.ScalarQueryParameter("group_claim", "TIMESTAMP", group_claim),
        bq.ScalarQueryParameter("claim", "TIMESTAMP", claim),
        bq.ScalarQueryParameter("invocation_end", "TIMESTAMP", res.best["end"]),
        bq.ScalarQueryParameter("m", "INT64", CLAIM_TIMEOUT_MINUTES)])
    return claim if n == 1 else None


def release_claim(ctx, row, claim, best=None):
    """Release a completed or fully recorded partial export."""
    from google.cloud import bigquery as bq
    params = [bq.ScalarQueryParameter("table_name", "STRING", row["table_name"]),
              bq.ScalarQueryParameter("claim", "TIMESTAMP", claim)]
    sets = "claimed_at = NULL"
    if best is not None:
        sets += ", last_invocation_id = @invocation_id, last_invocation_end = @invocation_end"
        params += [bq.ScalarQueryParameter("invocation_id", "STRING", best["id"]),
                   bq.ScalarQueryParameter("invocation_end", "TIMESTAMP", best["end"])]
    n = ctx.dml(f"""UPDATE `{PROJECT}.{DATASET}.mart_export_config` SET {sets}
                    WHERE table_name = @table_name AND claimed_at = @claim
                      AND recovery_started_at IS NULL""", params, deadline=cleanup_deadline())
    if n != 1:
        raise RuntimeError(f"claim on {row['table_name']} was lost or recovery is incomplete")


def clear_recovery(ctx, row, claim):
    from google.cloud import bigquery as bq
    n = ctx.dml(f"""UPDATE `{PROJECT}.{DATASET}.mart_export_config`
                    SET recovery_started_at = NULL, recovery_until = NULL
                    WHERE table_name = @table_name AND claimed_at = @claim""", [
        bq.ScalarQueryParameter("table_name", "STRING", row["table_name"]),
        bq.ScalarQueryParameter("claim", "TIMESTAMP", claim)])
    if n != 1:
        raise RuntimeError(f"claim on {row['table_name']} was lost during recovery")


MERGE_SQL = f"""
MERGE `{PROJECT}.{DATASET}.mart_sent_state` AS t
USING `{{source}}` AS s
ON t.table_name = @table_name AND t.row_key = s.row_key
WHEN MATCHED AND s.row_hash IS NULL THEN
  DELETE
WHEN MATCHED THEN
  UPDATE SET row_hash = s.row_hash, invocation_id = @invocation_id, sent_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED AND s.row_hash IS NOT NULL THEN
  INSERT (table_name, row_key, row_hash, invocation_id, sent_at)
  VALUES (@table_name, s.row_key, s.row_hash, @invocation_id, CURRENT_TIMESTAMP())
"""


def merge_sent_state(ctx, table_name, invocation_id, source_table, deadline=None):
    """MERGE (row_key, row_hash) rows of a table into mart_sent_state; row_hash NULL = DELETE."""
    from google.cloud import bigquery as bq
    params = [bq.ScalarQueryParameter("table_name", "STRING", table_name),
              bq.ScalarQueryParameter("invocation_id", "STRING", invocation_id)]
    retry_concurrent(lambda: ctx.query(MERGE_SQL.format(source=source_table), params, deadline=deadline), deadline)


def record_rows(ctx, table_name, invocation_id, rows, tag):
    """rows = [(row_key, row_hash or None)]: load them into a staging table, MERGE, drop it."""
    from google.cloud import bigquery as bq
    import io
    source = staging_name(table_name, f"sent_{tag}_")
    payload = "\n".join(json.dumps({"row_key": k, "row_hash": h}) for k, h in rows).encode("utf-8")
    job_config = bq.LoadJobConfig(
        source_format=bq.SourceFormat.NEWLINE_DELIMITED_JSON, write_disposition="WRITE_TRUNCATE",
        schema=[bq.SchemaField("row_key", "STRING"), bq.SchemaField("row_hash", "INT64")])
    ctx.bq.load_table_from_file(
        io.BytesIO(payload), source, job_config=job_config,
        timeout=remaining(record_deadline()), num_retries=0).result(
            timeout=remaining(record_deadline()), retry=None)
    try:
        merge_sent_state(ctx, table_name, invocation_id, source, deadline=record_deadline())
    finally:
        ctx.bq.delete_table(source, not_found_ok=True, timeout=remaining(cleanup_deadline()), retry=None)
    log("INFO", "recorded in mart_sent_state", table=table_name, rows=len(rows))


def wait_backlog_zero(sub_id, deadline, published_until):
    """Waits until the record subscription has no undelivered messages (two distinct fresh samples)."""
    from google.cloud import monitoring_v3
    client = monitoring_v3.MetricServiceClient()
    zero_reads = set()
    while True:
        remaining(deadline)
        end = now_utc()
        series = client.list_time_series(request={
            "name": f"projects/{PROJECT}",
            "filter": ('metric.type="pubsub.googleapis.com/subscription/num_undelivered_messages" '
                       f'AND resource.labels.subscription_id="{sub_id}"'),
            "interval": {"end_time": end, "start_time": end - timedelta(minutes=10)},
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL},
            timeout=remaining(deadline), retry=None)
        points = [p for s in series for p in s.points]
        if points:
            newest = max(points, key=lambda p: p.interval.end_time)
            stamp = newest.interval.end_time
            if (stamp > published_until and stamp >= end - timedelta(minutes=2)
                    and newest.value.int64_value == 0):
                zero_reads.add(stamp)
                if len(zero_reads) >= 2:
                    return
            else:
                zero_reads.clear()
        time.sleep(min(20, remaining(deadline)))


def recover_from_record(ctx, row, since, published_until, invocation_id):
    """The previous run on this table died: what Pub/Sub accepted is what the record subscription
    wrote. The newest message per row_key since the dead claim started goes into mart_sent_state
    (message_id de-duplicates the at-least-once record; row_hash = fingerprint of the data text)."""
    from google.cloud import bigquery as bq, pubsub_v1
    record = ctx.bq.get_table(f"{PROJECT}.{RECORD_TABLE}", timeout=remaining(), retry=None)
    partitioning = record.time_partitioning
    if (partitioning is None or partitioning.type_ != "DAY"
            or partitioning.field != "publish_time" or partitioning.expiration_ms is None):
        raise RuntimeError("record recovery requires daily publish_time partitions with retention")
    required_start = since - timedelta(minutes=2)
    partition_start = required_start.replace(hour=0, minute=0, second=0, microsecond=0)
    expires = partition_start + timedelta(milliseconds=partitioning.expiration_ms)
    if expires <= now_utc() + timedelta(seconds=remaining(cleanup_deadline())):
        raise RuntimeError(f"record recovery interval for {row['table_name']} is no longer retained")
    sub_id = RECORD_SUB_PREFIX + row["topic"]
    with pubsub_v1.SubscriberClient() as subscriber:
        subscription = subscriber.get_subscription(
            request={"subscription": f"projects/{PROJECT}/subscriptions/{sub_id}"},
            timeout=remaining(), retry=None)
    subscription_expires = required_start + subscription.message_retention_duration
    if subscription_expires <= now_utc() + timedelta(seconds=remaining(cleanup_deadline())):
        raise RuntimeError(f"record subscription recovery interval for {row['table_name']} is no longer retained")
    wait_backlog_zero(sub_id, min(START + STOP_AFTER_SECONDS, time.monotonic() + RECOVERY_WAIT_SECONDS),
                      published_until)
    source = staging_name(row["table_name"], "rec_")
    prefix = r'^\{"table":.*?,"operation":"[A-Z]+","primary_key":'
    ctx.query(f"""
      CREATE OR REPLACE TABLE `{source}` AS
      WITH r AS (
        SELECT message_id, publish_time, data
        FROM `{PROJECT}.{RECORD_TABLE}`
        WHERE subscription_name = @sub AND publish_time >= @since
        QUALIFY ROW_NUMBER() OVER (PARTITION BY message_id ORDER BY publish_time) = 1
      ), p AS (
        SELECT message_id, publish_time,
          JSON_VALUE(data, '$.operation') AS operation,
          REGEXP_EXTRACT(data, r'{prefix}(.*?),"data":') AS row_key,
          REGEXP_EXTRACT(data, r'{prefix}.*?,"data":(.*)\\}}$') AS data_text
        FROM r
      )
      SELECT row_key, IF(operation = 'DELETE', NULL, FARM_FINGERPRINT(data_text)) AS row_hash
      FROM p
      WHERE row_key IS NOT NULL
      QUALIFY ROW_NUMBER() OVER (PARTITION BY row_key ORDER BY publish_time DESC, message_id DESC) = 1""", [
        bq.ScalarQueryParameter("sub", "STRING", f"projects/{PROJECT}/subscriptions/{sub_id}"),
        bq.ScalarQueryParameter("since", "TIMESTAMP", required_start)])
    try:
        count = ctx.bq.get_table(source, timeout=remaining(), retry=None).num_rows
        if count:
            merge_sent_state(ctx, row["table_name"], invocation_id, source)
        log("INFO", "recovered from the record subscription", table=row["table_name"], rows=count,
            since=since)
    finally:
        ctx.bq.delete_table(source, not_found_ok=True, timeout=remaining(cleanup_deadline()), retry=None)


class Publisher:
    """Publishes messages with the library's 1,000-message batches; bookkeeping of what Pub/Sub accepted."""

    def __init__(self, ctx, table_name, topic, invocation_id):
        from google.cloud import pubsub_v1
        from google.api_core.retry import Retry
        self.ctx, self.table_name, self.invocation_id = ctx, table_name, invocation_id
        self.client = pubsub_v1.PublisherClient(batch_settings=pubsub_v1.types.BatchSettings(
            max_messages=BATCH_MESSAGES, max_bytes=9 * 1024 * 1024, max_latency=0.05))
        self.publish_retry = Retry()
        self.topic_path = self.client.topic_path(PROJECT, topic)
        self.cond = threading.Condition()
        self.outstanding = 0
        self.sent = []          # (row_key, row_hash) accepted by Pub/Sub, not yet in mart_sent_state
        self.sent_total = 0
        self.recorded = 0
        self.error = None
        self.merges = ThreadPoolExecutor(max_workers=1)
        self.merge_futures = []
        self.merge_seq = 0

    def _done(self, key, h, future):
        try:
            future.result()
            ok = True
        except Exception as e:
            ok = False
            err = e
        with self.cond:
            self.outstanding -= 1
            if ok:
                self.sent.append((key, h))
                self.sent_total += 1
            elif self.error is None:
                self.error = err
            self.cond.notify_all()

    def publish(self, key, h, message):
        with self.cond:
            while self.outstanding >= MAX_OUTSTANDING and self.error is None:
                self.cond.wait(min(1, remaining()))
            remaining()
            if self.error is not None:
                return False
            self.outstanding += 1
        try:
            future = self.client.publish(
                self.topic_path, message.encode("utf-8"), retry=self.publish_retry.with_timeout(min(60, remaining())), timeout=min(30, remaining()))
        except Exception:
            with self.cond:
                self.outstanding -= 1
            raise
        future.add_done_callback(lambda f, k=key, v=h: self._done(k, v, f))
        if len(self.sent) >= RECORD_EVERY_ROWS:
            self.flush_record()
        return True

    def flush_record(self):
        with self.cond:
            rows, self.sent = self.sent, []
        if not rows:
            return
        self.merge_seq += 1
        self.recorded += len(rows)
        self.merge_futures.append(self.merges.submit(
            record_rows, self.ctx, self.table_name, self.invocation_id, rows, str(self.merge_seq)))

    def finish(self):
        """Waits for every publish, records the rest and waits for all MERGEs; raises on any failure."""
        deadline = min(START + STOP_AFTER_SECONDS + 60, record_deadline() - 60)
        with self.cond:
            while self.outstanding > 0 and time.monotonic() < deadline:
                self.cond.wait(1)
            if self.outstanding > 0 and self.error is None:
                self.error = RuntimeError(f"{self.outstanding} publishes unfinished at the time limit")
        self.flush_record()
        try:
            for f in self.merge_futures:
                f.result(timeout=remaining(record_deadline()))
        finally:
            self.merges.shutdown(wait=False, cancel_futures=True)
        if self.error is not None:
            raise RuntimeError(f"publish failed: {type(self.error).__name__}: {self.error}")


def send_table(ctx, row, res, group_claim):
    """Returns 'sent' (checkpoint moved), 'partial' (stopped at the time limit) or 'skipped'."""
    from google.cloud import bigquery as bq
    from google.cloud.bigquery_storage_v1 import BigQueryReadClient, types
    from google.api_core.exceptions import DeadlineExceeded
    name, best = row["table_name"], res.best
    prev_claim = row["claimed_at"]
    since = row["recovery_started_at"] or prev_claim
    published_until = row["recovery_until"]
    if prev_claim is not None:
        published_until = max(published_until or prev_claim, prev_claim + timedelta(minutes=30))
    claim = claim_table(ctx, row, res, group_claim)
    if claim is None:
        log("INFO", "claimed elsewhere or already handled", table=name, invocation=best["id"])
        return "skipped"
    log("INFO", "exporting", table=name, invocation=best["id"], scheduler=best["scheduler"],
        recovering=prev_claim is not None)
    publisher = None
    recovery_complete = since is None
    try:
        if since is not None:
            recover_from_record(ctx, row, since, published_until, best["id"])
            clear_recovery(ctx, row, claim)
            recovery_complete = True
        sql = open(DIFF_SQL, encoding="utf-8").read().replace("{{dataset}}", f"{PROJECT}.{DATASET}") \
            .replace("{{source_view}}", row["source_view"])
        staging = staging_name(name, "stg_")
        ctx.query(f"""CREATE OR REPLACE TABLE `{staging}` AS
                      SELECT row_key, row_hash, message FROM (
                      {sql}
                      )""", [bq.ScalarQueryParameter("table_name", "STRING", name)])
        total = ctx.bq.get_table(staging, timeout=remaining(), retry=None).num_rows
        log("INFO", "diff ready", table=name, rows=total)
        publisher = Publisher(ctx, name, row["topic"], best["id"])
        stopped = False
        try:
            if total:
                reader = BigQueryReadClient()
                _, dataset_id, table_id = staging.split(".")
                session = reader.create_read_session(
                    parent=f"projects/{PROJECT}",
                    read_session=types.ReadSession(
                        table=f"projects/{PROJECT}/datasets/{dataset_id}/tables/{table_id}",
                        data_format=types.DataFormat.AVRO,
                        read_options=types.ReadSession.TableReadOptions(
                            selected_fields=["row_key", "row_hash", "message"])),
                    max_stream_count=1, timeout=remaining(), retry=None)
                for stream in session.streams:
                    for r in reader.read_rows(stream.name, timeout=remaining(), retry=None).rows(session):
                        remaining()
                        if not publisher.publish(r["row_key"], r["row_hash"], r["message"]):
                            break
                    if publisher.error is not None:
                        break
        except (TimeoutError, DeadlineExceeded):
            if elapsed() < STOP_AFTER_SECONDS:
                raise
            stopped = True
        finally:
            publisher.finish()
        ctx.bq.delete_table(staging, not_found_ok=True, timeout=remaining(cleanup_deadline()), retry=None)
        if stopped:
            release_claim(ctx, row, claim)                # last_invocation_* stays: next check sends the rest
            msg = (f"{name} stopped at the {STOP_AFTER_SECONDS // 60}-minute limit: sent "
                   f"{publisher.sent_total} of {total} rows, recorded; the next check run continues")
            log("WARNING", msg, table=name, sent=publisher.sent_total, total=total)
            ctx.slack(f":warning: datamart-publish {msg}")
            return "partial"
        release_claim(ctx, row, claim, best=best)
        log("INFO", "sent", table=name, rows=publisher.sent_total, invocation=best["id"])
        return "sent"
    except (TimeoutError, DeadlineExceeded):
        if publisher is None and recovery_complete and elapsed() >= STOP_AFTER_SECONDS:
            release_claim(ctx, row, claim)
            return "partial"
        raise


def send_main():
    ctx = Context()
    failed = []
    try:
        handled = set()
        log("INFO", "send task started", task=os.environ.get("CLOUD_RUN_TASK_INDEX"),
            tasks=os.environ.get("CLOUD_RUN_TASK_COUNT"))
        while elapsed() < STOP_AFTER_SECONDS:
            groups = ordered_groups(ctx.read_config())
            pick = None
            for group, members in groups.items():
                if group in handled or all(r["seeded_at"] is None for r in members):
                    continue                           # nothing to send: not claimed, not released
                claim = claim_group(ctx, group)
                if claim is not None:
                    pick = group, claim
                    break
            if pick is None:
                break
            group, group_claim = pick
            handled.add(group)
            try:
                members = ordered_groups(ctx.read_config())[group]
                log("INFO", "group taken", group=group, tables=[r["table_name"] for r in members])
                for row in members:
                    if elapsed() >= STOP_AFTER_SECONDS:
                        break
                    if row["seeded_at"] is None:
                        continue
                    try:
                        res = resolve(ctx, row)
                        if res.kind == "advance":
                            advance_only(ctx, row, res.newest)
                        elif res.kind == "send":
                            send_table(ctx, row, res, group_claim)
                    except Exception as e:
                        failed.append(f"{row['table_name']}: {type(e).__name__}: {e}")
                        log("ERROR", "table failed", table=row["table_name"], error=str(e))
            finally:
                try:
                    release_group(ctx, group, group_claim)
                except Exception as e:                 # claim expiry allows later tasks to reclaim the group
                    log("WARNING", "group release failed, the claim expires by itself", group=group,
                        error=str(e))
    except Exception as e:
        failed.append(f"send task: {type(e).__name__}: {e}")
        log("ERROR", "send task failed", error=str(e))
    if failed:
        ctx.slack(
            f":red_circle: datamart-publish send task {os.environ.get('CLOUD_RUN_TASK_INDEX', '?')} "
            f"(execution {os.environ.get('CLOUD_RUN_EXECUTION', '?')}) failed; "
            + "; ".join(failed))
    log("INFO", "send task finished", failed=failed, seconds=int(elapsed()))
    return 1 if failed else 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "check":
        return check_main()
    if mode == "send":
        return send_main()
    print("usage: main.py check|send", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

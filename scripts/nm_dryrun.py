#!/usr/bin/env python3
"""BigQuery DRY RUN of compiled Dataform actions (used by scripts/nm-lint.sh).

Safety: the only BigQuery call is Client.query(..., dry_run=True) against the pinned
project. Nothing is executed or written. Any action targeting another project is refused.
"""
import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

PROJECT = "databuffet-nonprd"
# Changes here can alter every action, so they widen the check to all actions.
WIDE_PREFIXES = ("includes/", "workflow_settings.yaml")
MISSING_TABLE = re.compile(r"Not found: (?:Table|View) `?([\w-]+)[:.]([\w-]+)\.([\w-]+)`?(?=\s|$)", re.I)
SQL_QUOTED_OR_COMMENT = re.compile(
    r"--[^\n]*|\#[^\n]*|/\*.*?\*/|'''(?:\\.|[^\\])*?'''|\"\"\"(?:\\.|[^\\])*?\"\"\"|"
    r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`",
    re.S,
)


def action_queries(a, is_op):
    """Return [(label, sql, requires_materialized_target)] for one compiled action."""
    if is_op:
        return [("operation", q, False) for q in a.get("queries", [])]
    out = []
    for label, key, pre_key, post_key in (
        ("query", "query", "preOps", "postOps"),
        ("incremental", "incrementalQuery", "incrementalPreOps", "incrementalPostOps"),
    ):
        sql = a.get(key)
        if sql:
            post = [s for s in a.get(post_key, []) if s.strip()]
            sequence = [s for s in a.get(pre_key, []) + [sql] + post if s.strip()]
            sql = ";\n".join(sequence)
            needs_target = bool(post)
            if (sql, needs_target) not in [(q, needs) for _, q, needs in out]:
                out.append((label, sql, needs_target))
    return out


def is_unverified_script(sql):
    text = SQL_QUOTED_OR_COMMENT.sub(" ", sql)
    statements = [s.strip() for s in text.split(";") if s.strip()]
    unsupported = r"^(?:BEGIN|DECLARE|CALL|EXECUTE\s+IMMEDIATE|IF|FOR|WHILE|LOOP|REPEAT|CREATE\s+(?:OR\s+REPLACE\s+)?TEMP(?:ORARY)?\s+TABLE)\b"
    return any(re.match(unsupported, s, re.I) for s in statements) or any(
        re.match(r"^(?:CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE)\b", s, re.I)
        for s in statements[:-1]
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compile", required=True)
    ap.add_argument("--changed", required=True)
    ap.add_argument("--mode", choices=("changed", "all"), required=True)
    args = ap.parse_args()

    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError
        from google.cloud import bigquery
    except ImportError as e:
        print(f"nm-lint: FAIL dry run - cached BigQuery client unavailable: {e}")
        return 1
    try:
        creds, _ = google.auth.default()
    except DefaultCredentialsError as e:
        if str(e).startswith("Your default credentials were not found."):
            print("nm-lint: WARNING: SKIP dry run - no application default credentials found; SQL is UNVERIFIED")
            return 0
        print(f"nm-lint: FAIL dry run - invalid application default credentials: {e}")
        return 1
    except Exception as e:
        print(f"nm-lint: FAIL dry run - credential discovery failed: {e}")
        return 1
    try:
        client = bigquery.Client(project=PROJECT, credentials=creds)
    except Exception as e:
        print(f"nm-lint: FAIL dry run - BigQuery client creation failed: {e}")
        return 1

    g = json.load(open(args.compile))
    changed = {l.strip() for l in open(args.changed) if l.strip()}
    if args.mode == "changed" and any(c.startswith(WIDE_PREFIXES) for c in changed):
        print("nm-lint: includes/ or workflow_settings.yaml changed - checking all actions")
        args.mode = "all"

    targets = {
        (a["target"]["database"], a["target"]["schema"], a["target"]["name"])
        for key in ("tables", "operations", "assertions")
        for a in g.get(key, [])
    }
    items = []
    for key, is_op in (("tables", False), ("operations", True)):
        for a in g.get(key, []):
            if args.mode == "changed" and a.get("fileName") not in changed:
                continue
            t = a["target"]
            if t.get("database") != PROJECT:
                print(f"nm-lint: REFUSED - {a.get('fileName')} targets project {t.get('database')!r}, only {PROJECT} is allowed")
                return 1
            for label, sql, needs_target in action_queries(a, is_op):
                items.append((a["fileName"], label, sql, needs_target))

    print(f"nm-lint: dry-running {len(items)} queries ({args.mode} actions) on {PROJECT}")
    cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

    def run(it):
        f, label, sql, needs_target = it
        if needs_target:
            return it, "unverified", "post-operations require the newly materialized target; its schema is not validated by this dry run"
        if is_unverified_script(sql):
            return it, "unverified", "multi-statement/script SQL cannot be fully validated by BigQuery dry run"
        try:
            job = client.query(sql, job_config=cfg, project=PROJECT)
            return it, "ok", job.total_bytes_processed or 0
        except Exception as e:
            msg = getattr(e, "message", None) or str(e)
            missing = MISSING_TABLE.findall(msg)
            return it, ("warn" if missing and all(t in targets for t in missing) else "fail"), msg

    oks = fails = warns = unverified = 0
    total = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for (f, label, _, _), status, val in ex.map(run, items):
            if status == "ok":
                oks += 1
                total += val
                print(f"  ok    {f} [{label}] would process {val:,} bytes")
            elif status == "warn":
                warns += 1
                print(f"  WARN  {f} [{label}] skipped (compiled action target not in BigQuery yet): {val.splitlines()[0][:200]}")
            elif status == "unverified":
                unverified += 1
                print(f"  UNVERIFIED  {f} [{label}]: {val}")
            else:
                fails += 1
                print(f"  FAIL  {f} [{label}]: {val.strip()[:600]}")
    print(f"nm-lint: {len(items)} queries, {oks} ok, {fails} failed, {warns} skipped with warning, {unverified} unverified, {total:,} bytes total (dry run, nothing executed)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

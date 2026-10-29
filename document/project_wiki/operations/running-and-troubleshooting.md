# Running & Troubleshooting

> **LLM context**: How to execute and debug this project. Local validation, cached
> tooling, credential handling, and execution constraints are owned by the
> [run/debug guide](../../how-to/run-and-debug.md).
> Ad-hoc queries: `bq --project_id=databuffet-nonprd` (default gcloud project differs!).

## Run graph by tag

| Tag | What runs |
|---|---|
| `initial` | ⚠️ **Destructive.** Recreates the raw external tables **and** drops validated tables of cis360, mastersku, master_sku, saleout_mdt, allkons_commission and derp. Exact drop scope: [initial file map](../initial/initial-layer.md#file-map). See the warning below |
| `re-initial` | ⚠️ DROP validated/curated MAC5 tables (destructive, mac5 only) |
| `validated` / `validated_full` / `validated_incremental` | Validated layer |
| `curated` / `curated_full` / `curated_incremental` | Curated layer (the sub-tags are used by the SALEOUT_MDT curated files) |
| `dimension_daily` | Every dim except `dim_calendar`, plus the [org center](../org_center/org-center.md) tables (`org_center_schema`, `org_center_unit`, `org_center_member`) |
| `dimension_yearly` | `dim_calendar` only |
| `fact_daily` | Every fact |
| `cdc` / `cdc_incremental` | CDC change log |
| `process` | AI address parsing (`deb_address_data`) + RLS access map (`rls_customer360`) |
| `pub_sub` | Pub/Sub pilot objects (`pub_sub` dataset, export views, `mart_export_config`, `mart_sent_state`). No scheduler runs it — run by hand; [process reference](../cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) |

Unused-but-defined: `dimension_monthly`, `fact_monthly`, `fact_yearly`.
There is **no** `assertions` tag. Per-tag file counts: see the
[generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview).

> ⚠️ **Never run the whole `initial` tag to add or refresh one raw table.**
> For raw setup, dependency safety, and manual rebuilds, follow the
> [initial-layer guide](../initial/initial-layer.md#การผูก-dependency). The schema and UDF files
> (`create_all_schema`, `create_all_function`) have no tag; run them by action name.

## Schedule (Dataform service, `databuffet-nonprd`)

Read from the Dataform API (`releaseConfigs` / `workflowConfigs`) on 2026-10-18.
Nothing in git records this; the config lives in the Dataform UI.

| Item | When (cron, timezone) | What it does |
|---|---|---|
| Release config `production` | 05:45 daily (`45 5 * * *`, Asia/Bangkok) | Compiles the **`nonprod`** branch. No vars override, so `workflow_settings.yaml` on `nonprod` is what runs |
| Workflow `daily_process` | 06:00 daily (`0 6 * * *`, Asia/Bangkok) | Tags `validated`, `curated`, `dimension_daily`, `fact_daily`, `cdc_incremental`, `process`. No transitive dependencies |
| Workflow `saleout_morning` | 08:55 daily (`55 8 * * *`, Asia/Bangkok) | 31 explicitly listed SALEOUT_MDT targets (list below). No tags, no transitive dependencies. Purpose not recorded |
| Workflow `yearly_process` | Dec 15, 12:00 (`0 12 15 12 *`, **Asia/Jakarta**) | Tag `dimension_yearly` (`dim_calendar`). Runs as a personal user account, not a service account |
| Cloud Run `alert-dataform` | 07:00 daily | Writes the run result to `monitor_dataset.dataform_run_action` (skill `check-runs`) |

Consequences:

- `view`, `initial`, `re-initial` and `cdc` are **not scheduled on purpose**.
  Presentation views are deployed by hand ([deploy-view guide](../../how-to/deploy-view.md));
  the Pub/Sub pilot objects use tag `pub_sub`, also run by hand (below).
- A var change (e.g. `BACKFILL_DAYS`) only reaches the nightly if it is committed on
  **`nonprod` before 05:45**. A change in a workspace or on `dev` alone does nothing.
- `saleout_morning` re-runs the SALEOUT_MDT chain after `daily_process`. Its targets:
  - schemas: `validated_schema_saleout`, `curated_schema_saleout`;
  - validated (13 of 16 tables): `eom_bt`, `eom_gb`, `eom_hp`, `eom_tw`,
    `report_sale_subscription`, `sale_by_branch_detail`, `sale_by_branch_mch3`,
    `saleout_dh`, `saleout_gb`, `saleout_hp`, `saleout_lastyear`, `stock_aging`,
    `stock_by_branch` (not in the list: `sales_by_branch`, `turnover`, `turnover_brand`);
  - curated: `curated_saleout_mdt`, `curated_stock_mdt`, `curated_saleout_monthly_mdt`;
  - dims: `dim_pc`, `dim_product_mdt`, `dim_sales_branch_mdt`, `dim_target_saleout_mdt`,
    `dim_target_series_mdt`, `dim_zone_mdt`, `dim_zone_ta_mdt`;
  - facts: `fact_saleout_mdt`, `fact_saleout_monthly_mdt`, `fact_stock_mdt`,
    `fact_stock_mdt_monthly`, `fact_target_saleout_mdt`, `fact_target_series_mdt`.

  The list is explicit, so **a new SALEOUT_MDT table must be added to it by hand** in
  the Dataform UI, or it runs only at 06:00.
- The Pub/Sub pilot needs **no change to any workflow configuration**. Follow the
  [pilot deployment steps](../cdc-process/process.md#deploy)
  for the required live-compilation check and manual deployment. The
  [process reference](../cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)
  owns the config lifecycle, tables, duplicate guard and publishing behavior.
- DERP (`validated_derp`) runs in `daily_process` (tag `validated`) from 2026-10-18.
  Its GCS files for `ASATDATE=D` land at about 01:02 Bangkok on D+1. It is not in
  `saleout_morning`.
- When a source is first built by hand and then wired into the schedule, check the
  first window: with `BACKFILL_DAYS = 1` the nightly reads only from yesterday, so a
  partition that landed after the hand build and before yesterday is skipped for good.

For local commands see [README — Common Commands](../../../README.md#common-commands);
for executing tags/actions see the [run guide](../../how-to/run-and-debug.md#รันด้วย-tag).

## Ad-hoc BigQuery from local WSL

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false 'SELECT ...'
```
- Region-level `INFORMATION_SCHEMA` is permission-denied; use **dataset-level**:
  `` `databuffet-nonprd.dimension_table.INFORMATION_SCHEMA.COLUMNS` ``.
- Default gcloud project is a different one — always pass `--project_id`.

## Common failure modes

| Symptom | Likely cause / fix |
|---|---|
| Dim MERGE fails: table not found | `type: "operations"` targets pre-exist in BigQuery — a brand-new dim table must be created (DDL) before its first MERGE run |
| Duplicate SK rows | `max_sk` raced or MERGE ON mismatch; check the t2/t3 CASE and that MERGE is `ON T.<X>SK = S.<X>SK` |
| Dim missing recent mds edits | `MDS_BACKFILL_DAYS` window (currently 1 day) — a row updated earlier but missed needs a manual backfill run with a larger var value |
| Validated datetime parse fails | Raw extract switched timestamp format; `parseFlexibleDatetime` handles the two known formats — check for a third (see 2026-05-23/24 incident, self-resolved) |
| Validated incremental missed data | The window is `ASATDATE >= CURRENT_DATE - BACKFILL_DAYS` (string compare, default 1 day) — for older data raise `BACKFILL_DAYS` and rerun (see below) |
| PK post-op ALTER fails repeatedly | BigQuery metadata contention — the retry loop (10×) usually recovers; rerun otherwise |
| Fact upsert doubles rows | `fact_transcation` DELETE keys are `milVnos, milType, CompanySK` — grain drift in `onetime.Transaction_Data_Mart` breaks this |
| Orphan SK values in facts | Expected after mds hard-deletes ([mds-delete-pattern.md](../dimension/mds-delete-pattern.md)); `dim_target_product_group_by_sale*` self-heal next day |

## Drift: views/UDFs edited in the BigQuery console

Views and UDFs get edited directly in the console and the change never reaches
`definitions/`. Either the next Dataform run silently overwrites the console
work, or the repo carries SQL that no longer matches production.

**BigQuery is the source of truth for view SQL.** Pull the console version into
the repo; do not push the repo over a live view unless that is the explicit
intent.

Run the scan before any `view` tag run, and after a stretch of console work:
skill `bq-drift-scan` (`.claude/skills/bq-drift-scan/`, with
`scripts/{dump.sql,scan.py,pull.py}`), or the read-only `bq-drift-auditor` agent.
Baseline 2026-09-15 (ปิดท้ายวัน): **40 objects, 40 identical, 0 different** — the first
clean scan on record. Five views were cleared that day: `view_dim_aging_history`
(stale 5 weeks), `Model_Invoice_Transaction` (stale 5 months), `Transaction_Data_Mart`,
`view_fact_transcation`, and `view_dim_invoice` (console edited to match the repo).
`onetime.PowerBI_Data_Buffet_Transaction` shows as
"extra in BigQuery" because the `.sqlx` was moved to `backup/` on 2026-09-03 --
deleting the file does not drop the live view. `onetime` holds exactly the 6 views the repo
builds — no untracked leftovers.

Things that cost time the first round:

- `INFORMATION_SCHEMA.VIEWS.view_definition` returns table paths **without
  backticks**. It still runs (GoogleSQL accepts a hyphenated project id unquoted),
  but it breaks the repo convention — re-add `` `${XxxTableRef}` `` when pulling.
  A diff that normalises backticks away cannot see this; check it separately.
- Saving a view in the console **drops commented-out blocks**. `view_rls_data`
  lost 88 lines that way; the text is still in git history.
- BigQuery ids are **case sensitive**. `RLS_Customer360` vs `rls_customer360`
  compiles and fails at run time — confirm with `bq ls <dataset>`.
- `last_modified_time` from `<dataset>.__TABLES__` (views) and
  `ROUTINES.last_altered` (UDFs), compared against `git log -1` for the file,
  is what tells you which side is ahead.

## Backfilling more than one day (`BACKFILL_DAYS`)

Every validated and curated incremental window reads
`DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY)`
The var is committed in `workflow_settings.yaml` (`BACKFILL_DAYS: "1"`).
`databuffet.js` falls back to `"1"` — yesterday only — when it is absent.

When a source has been failing for several days — say `mih` has been broken for
three — widen the window instead of doing a full refresh:

1. Edit `workflow_settings.yaml` in a Dataform workspace:
   `BACKFILL_DAYS: "3"`
2. Compile and check **Compiled queries** — the window should read `INTERVAL 3 DAY`.
3. Run the affected actions (or the `validated` / `curated` tags) from that workspace.
4. **Set it back to `"1"`** and re-run nothing.

The schedule does not use workspaces. It compiles the `nonprod` branch at 05:45
(see [Schedule](#schedule-dataform-service-databuffet-nonprd)). To widen the
nightly window instead, commit the change on `nonprod` before 05:45 and revert it
after the run.

Notes:

- The window is a look-back from today, not a date range. `"3"` means the last
  three days, so it always includes yesterday.
- Widening it costs a proportional scan of the raw partitions — the tables are
  partitioned on `asatdate`, so 3 days is roughly 3× the bytes, not a full scan.
- `QUALIFY ROW_NUMBER() ... ORDER BY asatdate DESC` still keeps one row per PK,
  so re-reading days that already landed is idempotent.
- **Left on the old hardcoded `-1` on purpose** (they mean something other than a
  look-back window, do not wire them to this var):
  `cdc_change_log.sqlx` (`=` a single partition, not a range),
  `dim_aging.sqlx` `run_date` (a snapshot date — widening it would DELETE more
  days than it re-INSERTs), and `view_fact_transcation` (the upper bound of a
  4-year range).

## Git / environments

- Branches: `dev` (working) and `nonprod` (what the schedule compiles), then `prod`;
  `hotfix` exists. Work reaches `nonprod` in two lanes, and commits can also land on
  `dev` directly: see the [release flow](../../getting-started/onboarding.md#release-flow).
- `workflow_settings.yaml` is per-environment (project id differs).
- The run monitor is live: Cloud Run `alert-dataform` writes
  `monitor_dataset.dataform_run_action` daily at 07:00 Bangkok (skill `check-runs`,
  details in [known-issues](../../operations/known-issues.md)).

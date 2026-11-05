---
type: BigQuery Table
title: "mart_export_config"
description: "One row = one Data Mart table exported to Pub/Sub, with its source view, topic, task group, trigger and the publisher's memory of the last Dataform run it handled."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=mart_export_config&page=table"
project_id: databuffet-nonprd
dataset_id: process_dataset
table_id: mart_export_config
tags: ["process", "pub_sub", "Pub/Sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/process/mart_export_config.sqlx"
    title: "Dataform definition (process/mart_export_config.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Configuration and state table of the Data Mart to Pub/Sub export: one row per exported table (dim_company, the commission sets, the TA app org tables and the AI team sample tables; table_name = the BigQuery table name in lower case, e.g. dim_calendar, view_dim_customer, fact_order, rls_ta_customer). The columns table_name, source_view, topic, trigger_scheduler and task_group come from `includes/controller/mart-export-config.json`; last_invocation_id, last_invocation_end and claimed_at are written by the first-load exporter and the Cloud Run publisher (job `datamart-publish-check` every 5 minutes starts job `datamart-publish-send`, both outside Dataform) to checkpoint the last Dataform workflow invocation handled and to claim the row while publishing. It is paired with [mart_sent_state](/process/mart_sent_state.md); the export views it points to live in dataset [pub_sub](/view/pub_sub/index.md), e.g. [export_dim_company](/view/pub_sub/export_dim_company.md) and [export_order](/view/pub_sub/export_order.md).

# Grain and key

One row = one Data Mart table exported to Pub/Sub: key `table_name` (the exported table = the message `table`). Dataform inserts new rows with a MERGE and updates only task_group of existing rows; every other existing config value, checkpoint and claim is preserved. seeded_at is backfilled only for tables that already have sent state.

# Schema

| Column | Type | Description |
|---|---|---|
| `table_name` | STRING | Exported table name = the Pub/Sub message `table` (e.g. dim_company, order); without trigger_scheduler also the Dataform action whose successful run triggers the export. Key of the table. |
| `source_view` | STRING | Full name of the export view in dataset pub_sub (databuffet-nonprd.pub_sub.export_<table>). |
| `topic` | STRING | Pub/Sub topic the changed rows are published to. |
| `last_invocation_id` | STRING | Publisher checkpoint: id (after workflowInvocations/) of the last Dataform workflow invocation already handled for this table; NULL before seeding; 'seed' after the first-load snapshot records its current rows, until a later export. |
| `last_invocation_end` | TIMESTAMP | End time (UTC) of that invocation, or the seed time for 'seed'; NULL before seeding or before the first export of a table without trigger_scheduler; only invocations that ended later count as new. |
| `claimed_at` | TIMESTAMP | Shared being-processed marker (UTC) set by the publisher or the first-load exporter; NULL = free; the publisher may reclaim a claim older than 35 minutes only for a seeded table. The first-load exporter requires NULL. |
| `trigger_scheduler` | STRING | Dataform workflow configuration whose SUCCEEDED invocations trigger the export ('daily_process' for the commission sets, the TA org sets and the AI team sample tables); NULL = a SUCCEEDED invocation whose action table_name SUCCEEDED (dim_company). |
| `seeded_at` | TIMESTAMP | NULL = not seeded; the publisher skips the table entirely regardless of claimed_at. The first-load export sets it to the export time in the seed transaction; tables that already have sent state are backfilled from MIN(sent_at). |
| `task_group` | STRING | Name of the group of tables one send task works through (e.g. fact_order, commission, master); the groups are taken in the order of the config JSON and a task claims the next group that still has a table to send. Refreshed from the JSON on every Dataform run. |
| `group_claimed_at` | TIMESTAMP | Group ownership marker, set atomically across every member only when no member has a live group or table claim. Released after the group; expires after 35 minutes if the task dies. |
| `recovery_started_at` | TIMESTAMP | Earliest unresolved dead table claim; retained across failed recovery and repeated reclaims until record recovery has merged into sent state. |
| `recovery_until` | TIMESTAMP | Latest dead table claim plus its 30-minute task limit; recovery requires two distinct, fresh zero-backlog samples after this timestamp. Cleared with recovery_started_at after the recovery MERGE. |

# How it is built

- Definition: `definitions/process/mart_export_config.sqlx` (`type: "operations"`, tags `pub_sub`); the operation owns this table.
- Reads: [mart_sent_state](/process/mart_sent_state.md), to backfill seeded_at; export-view names are resolved with `resolve()` (no dependency on the views, no view data read).
- Operations: `CREATE TABLE IF NOT EXISTS` with all 12 columns (never rebuilt, never altered), backfill seeded_at from MIN(sent_at) for tables with sent state, then MERGE from the JSON: a new row has NULL last_invocation_id/end, claimed_at and seeded_at; an existing row only gets task_group updated. Compilation fails when a JSON entry has no task_group.

# Examples

Export state and whether a run holds the claim.

```sql
SELECT table_name, source_view, topic, last_invocation_id,
       last_invocation_end, claimed_at, seeded_at,
       claimed_at IS NOT NULL AND claimed_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 35 MINUTE) AS is_claimed
FROM `databuffet-nonprd.process_dataset.mart_export_config`
```

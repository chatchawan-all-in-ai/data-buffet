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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Configuration and state table of the Data Mart to Pub/Sub export: dim_company (pilot), the 12 commission sets for the TF team (order, invoice, credit_note, debit_note, receipt, chqri, status, company, sell, warehouse, stk, company_source) and the 9 TA app org tables for the AI team (org_levels, org_units, positions, employees, memberships, appointments, member_links, access_exceptions, customer_ta_assignments) and the 33 AI team sample tables (one export per table of the 2026-10-26 package, the rls sample and the dashboard display control: table_name = the BigQuery table name in lower case, e.g. dim_calendar, view_dim_customer, fact_order, rls_ta_customer). The columns table_name, source_view, topic, trigger_scheduler and task_group come from `includes/controller/mart-export-config.json`; last_invocation_id, last_invocation_end and claimed_at are written by the first-load exporter and the Cloud Run publisher (job `datamart-publish-check` every 5 minutes starts job `datamart-publish-send`, both outside Dataform) to remember the last Dataform workflow invocation handled and to claim the row while publishing. It is paired with [mart_sent_state](/process/mart_sent_state.md); the export views it points to live in dataset [pub_sub](/view/pub_sub/index.md), e.g. [export_dim_company](/view/pub_sub/export_dim_company.md) and [export_order](/view/pub_sub/export_order.md).

# Grain and key

One row per `table_name` (the exported table = the message `table`). Dataform inserts new rows with a MERGE, updates only task_group of existing rows and backfills only seeded_at for existing sent state; it preserves every other existing config value, checkpoint and claim. 55 rows: dim_company, the 12 commission sets, the 9 TA org sets and the 33 AI team sample tables.

# Schema

| Column | Type | Description |
|---|---|---|
| `table_name` | STRING | Exported table name = the Pub/Sub message `table` (e.g. dim_company, order); without trigger_scheduler also the Dataform action whose successful run triggers the export. Key of the table. |
| `source_view` | STRING | Full name of the export view in dataset pub_sub (databuffet-nonprd.pub_sub.export_<table>); see name resolution below. |
| `topic` | STRING | Pub/Sub topic the changed rows are published to. |
| `task_group` | STRING | Name of the group of tables one send task works through (e.g. fact_order, commission, master); the groups are taken in the order of the config JSON and a task claims the next group that still has a table to send. Ninth column; refreshed from the JSON on every Dataform run. |
| `group_claimed_at` | TIMESTAMP | Group ownership marker, set atomically across every member only when no member has a live group or table claim. Released after the group; expires after 35 minutes if the task dies. |
| `recovery_started_at` | TIMESTAMP | Earliest unresolved dead table claim; retained across failed recovery and repeated reclaims until record recovery has merged into sent state. |
| `recovery_until` | TIMESTAMP | Latest dead table claim plus its 30-minute task limit; recovery requires two distinct, fresh zero-backlog samples after this timestamp. Cleared with recovery_started_at after the recovery MERGE. |
| `last_invocation_id` | STRING | Workflow memory: id (after workflowInvocations/) of the last Dataform workflow invocation already handled for this table; NULL before seeding; 'seed' after the first manual unseeded-table snapshot records its current rows, until a later export. |
| `last_invocation_end` | TIMESTAMP | End time (UTC) of that invocation, or the seed time for 'seed'; NULL before seeding or for the pilot before its first export; only invocations that ended later count as new. |
| `claimed_at` | TIMESTAMP | Shared being-processed marker (UTC) set by the publisher or the first-load exporter; NULL = free; the publisher may reclaim a claim older than 35 minutes only for a seeded table. The snapshot exporter requires NULL; see the first-load procedure in the [setup guide](../../how-to/setup-pubsub-export.md#3-โหลดครั้งแรกด้วยไฟล์-ครั้งแรกที่ทีมต่อ-topic-นั้นเท่านั้น). |
| `trigger_scheduler` | STRING | Dataform workflow configuration whose SUCCEEDED invocations trigger the export ('daily_process' for the commission sets, the TA org sets and the AI team sample tables); NULL = a SUCCEEDED invocation whose action table_name SUCCEEDED (dim_company). Seventh column. |
| `seeded_at` | TIMESTAMP | Eighth column, after trigger_scheduler. NULL = not seeded; publisher skips the table entirely regardless of claimed_at. First manual Cloud Shell export sets it to export time in the seed transaction. Existing tables with sent state (dim_company) are backfilled from MIN(sent_at). |

# How it is built

- Definition: `definitions/process/mart_export_config.sqlx` (`type: "operations"`, tags `pub_sub`); the operation owns this table.
- Creation defines all 12 columns together; an existing table must already have the complete schema because the operation does not alter it.
- Dependencies: [mart_sent_state](/process/mart_sent_state.md), read to backfill seeded_at. The operation does not read view data or write sent state.
- Export-view names use `resolve()` without adding dependencies, keeping this action within Dataform's 50-dependency limit. Compilation does not validate that these views exist. [`pubsub/scripts/setup.sh`](../../../pubsub/scripts/setup.sh) checks every configured export view exists in BigQuery and stops if one is missing; deployment prerequisites are in [setup guide A](../../how-to/setup-pubsub-export.md#ส่วน-a--deploy-และทดสอบ-pilot).
- Operations: `CREATE TABLE IF NOT EXISTS` with all 12 columns, backfill seeded_at from MIN(sent_at) for existing sent state, then MERGE from JSON: a new row has NULL last_invocation_id/end, claimed_at and seeded_at; an existing row only gets task_group updated, so its checkpoints and claims are preserved. Compilation fails when a JSON entry has no task_group. The publisher skips tables with seeded_at NULL. First-load execution and retry rules are in [setup guide B3](../../how-to/setup-pubsub-export.md#3-โหลดครั้งแรกด้วยไฟล์-ครั้งแรกที่ทีมต่อ-topic-นั้นเท่านั้น).
- Approximate size (BigQuery metadata, 2026-11-03): 13 rows (the tables deployed so far).

# Examples

Export state and whether a run holds the claim.

```sql
SELECT table_name, source_view, topic, last_invocation_id,
       last_invocation_end, claimed_at, seeded_at,
       claimed_at IS NOT NULL AND claimed_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 35 MINUTE) AS is_claimed
FROM `databuffet-nonprd.process_dataset.mart_export_config`
```

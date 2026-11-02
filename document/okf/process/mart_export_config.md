---
type: BigQuery Table
title: "mart_export_config"
description: "One row = one Data Mart table exported to Pub/Sub, with its source view, topic, trigger and the publisher's memory of the last Dataform run it handled."
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

Configuration and state table of the Data Mart to Pub/Sub export: dim_company (pilot) and the 12 commission sets for the TF team (order, invoice, credit_note, debit_note, receipt, chqri, status, company, sell, warehouse, stk, company_source). The columns table_name, source_view, topic and trigger_scheduler come from `includes/controller/mart-export-config.json`; last_invocation_id, last_invocation_end and claimed_at are written by the first-load exporter and the Cloud Workflow `datamart-publish` (runs every 5 minutes, outside Dataform) to remember the last Dataform workflow invocation handled and to claim the row while publishing. It is paired with [mart_sent_state](/process/mart_sent_state.md); the export views it points to live in dataset [pub_sub](/view/pub_sub/index.md), e.g. [export_dim_company](/view/pub_sub/export_dim_company.md) and [export_order](/view/pub_sub/export_order.md).

# Grain and key

One row per `table_name` (the exported table = the message `table`). Dataform inserts rows with an insert-only MERGE and backfills only seeded_at for existing sent state; it preserves existing config values, checkpoints and claims. 13 rows: dim_company and the 12 commission sets.

# Schema

| Column | Type | Description |
|---|---|---|
| `table_name` | STRING | Exported table name = the Pub/Sub message `table` (e.g. dim_company, order); without trigger_scheduler also the Dataform action whose successful run triggers the export. Key of the table. |
| `source_view` | STRING | Full name of the export view in dataset pub_sub (databuffet-nonprd.pub_sub.export_<table>), resolved by ref() at compile time. |
| `topic` | STRING | Pub/Sub topic the changed rows are published to. |
| `last_invocation_id` | STRING | Workflow memory: id (after workflowInvocations/) of the last Dataform workflow invocation already handled for this table; NULL before seeding; 'seed' after the first manual unseeded-table snapshot records its current rows, until a later export. |
| `last_invocation_end` | TIMESTAMP | End time (UTC) of that invocation, or the seed time for 'seed'; NULL before seeding or for the pilot before its first export; only invocations that ended later count as new. |
| `claimed_at` | TIMESTAMP | Shared being-processed marker (UTC) set by the publisher or the first-load exporter; NULL = free; the publisher may reclaim a claim older than 30 minutes only for a seeded table. The snapshot exporter requires NULL; see the first-load procedure in the [setup guide](../../how-to/setup-pubsub-export.md#3-โหลดครั้งแรกด้วยไฟล์-ครั้งแรกที่ทีมต่อ-topic-นั้นเท่านั้น). |
| `trigger_scheduler` | STRING | Dataform workflow configuration whose SUCCEEDED invocations trigger the export ('daily_process' for the commission sets); NULL = a SUCCEEDED invocation whose action table_name SUCCEEDED (dim_company). Seventh column, added by ALTER TABLE ADD COLUMN IF NOT EXISTS. |
| `seeded_at` | TIMESTAMP | Eighth column, after trigger_scheduler. NULL = not seeded; publisher skips the table entirely regardless of claimed_at. First manual Cloud Shell export sets it to export time in the seed transaction. Existing tables with sent state (dim_company) are backfilled from MIN(sent_at). |

# How it is built

- Definition: `definitions/process/mart_export_config.sqlx` (`type: "operations"`, tags `pub_sub`); the operation owns this table.
- Dependencies: every export view in dataset [pub_sub](/view/pub_sub/index.md), resolved by ref(), and [mart_sent_state](/process/mart_sent_state.md), read to backfill seeded_at. The operation does not read view data or write sent state.
- Operations: `CREATE TABLE IF NOT EXISTS`, append `trigger_scheduler` and `seeded_at` with ALTER, backfill seeded_at from MIN(sent_at) for existing sent state, then insert-only MERGE from JSON. New rows have NULL last_invocation_id/end, claimed_at and seeded_at; existing checkpoints and claims are preserved. The publisher skips tables with seeded_at NULL. First-load execution and retry rules are in [setup guide B3](../../how-to/setup-pubsub-export.md#3-โหลดครั้งแรกด้วยไฟล์-ครั้งแรกที่ทีมต่อ-topic-นั้นเท่านั้น).
- Approximate size (BigQuery metadata, 2026-10-31): 1 rows, 139 B.

# Examples

Export state and whether a run holds the claim.

```sql
SELECT table_name, source_view, topic, last_invocation_id,
       last_invocation_end, claimed_at, seeded_at,
       claimed_at IS NOT NULL AND claimed_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE) AS is_claimed
FROM `databuffet-nonprd.process_dataset.mart_export_config`
```

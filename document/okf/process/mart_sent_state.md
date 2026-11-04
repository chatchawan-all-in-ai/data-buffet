---
type: BigQuery Table
title: "mart_sent_state"
description: "One row = one data row (by row_key) that a Pub/Sub export table last sent successfully, with its hash and the Dataform invocation that sent it."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=mart_sent_state&page=table"
project_id: databuffet-nonprd
dataset_id: process_dataset
table_id: mart_sent_state
tags: ["process", "pub_sub", "Pub/Sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/process/mart_sent_state.sqlx"
    title: "Dataform definition (process/mart_sent_state.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Sent-state ledger of the Data Mart to Pub/Sub export: it holds, per export table, every row the receivers currently hold. The Cloud Run publisher (send job `datamart-publish-send`) diffs the export view (for dim_company: [export_dim_company](/view/pub_sub/export_dim_company.md)) against this table: a key absent here is NEW, a different `row_hash` is UPDATE, a key only here is DELETE. Writers are the publisher after successful delivery and the first-load exporter for an unseeded table (invocation_id 'seed'). Initialization status lives in [mart_export_config](/process/mart_export_config.md); the manual first-load and retry procedure is owned by [setup guide B3](../../how-to/setup-pubsub-export.md#3-โหลดครั้งแรกด้วยไฟล์-ครั้งแรกที่ทีมต่อ-topic-นั้นเท่านั้น).

# Grain and key

One row per `table_name` + `row_key` (neither NULL). `row_key` is `TO_JSON_STRING` of the export table's natural key columns (a NULL key component is JSON null inside the key object). Clustered by table_name, row_key.

# Schema

| Column | Type | Description |
|---|---|---|
| `table_name` | STRING | Exported table (matches mart_export_config.table_name). |
| `row_key` | STRING | JSON text of the row's natural key (export view's row_key), the message primary_key. |
| `row_hash` | INT64 | FARM_FINGERPRINT of the JSON of all data columns sent (export view's row_hash); a different hash means the row changed and is re-sent as UPDATE. |
| `invocation_id` | STRING | Dataform workflow invocation that sent the row, or 'seed' for a row recorded by its first manual unseeded-table snapshot. |
| `sent_at` | TIMESTAMP | UTC timestamp when the row was recorded as sent. |

# How it is built

- Definition: `definitions/process/mart_sent_state.sqlx` (`type: "operations"`, tags `pub_sub`); the operation owns this table.
- Reads: no other table; written by the publisher and, once per new export table, by the manual Cloud Shell `export-snapshot.sh` run for an unseeded table; never by tag pub_sub, setup, merge or deploy.
- Operations (`type: "operations"`, tag `pub_sub`, no scheduler runs it; deployed manually from `production` with dependencies off). `CREATE TABLE IF NOT EXISTS` only, never rebuilt; the publisher MERGEs into it (on table_name + row_key) every 1,000,000 sent rows and at the end of a table, and again when it recovers a crashed run from the record subscription; DELETEd keys are removed.

# Examples

Rows held per export table and the latest send time.

```sql
SELECT table_name, COUNT(*) AS rows_held, MAX(sent_at) AS last_sent_at
FROM `databuffet-nonprd.process_dataset.mart_sent_state`
GROUP BY table_name
```

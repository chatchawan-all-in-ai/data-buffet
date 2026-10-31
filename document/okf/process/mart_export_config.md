---
type: BigQuery Table
title: "mart_export_config"
description: "One row = one Data Mart table exported to Pub/Sub, with its source view, topic and the publisher's memory of the last Dataform run it handled."
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

Configuration and state table of the Data Mart to Pub/Sub export (currently only dim_company). The columns table_name, source_view and topic come from `includes/controller/mart-export-config.json`; the three remaining columns are written by the Cloud Workflow `datamart-publish` (runs every 5 minutes, outside Dataform) to remember the last Dataform workflow invocation handled and to claim the row while publishing. It is paired with [mart_sent_state](/process/mart_sent_state.md); the export view it points to is [export_dim_company](/view/pub_sub/export_dim_company.md).

# Grain and key

One row per `table_name` (the exported table, which is also the Dataform action whose successful run triggers an export). Rows are only ever inserted by Dataform (insert-only MERGE); existing rows are never overwritten.

# Schema

| Column | Type | Description |
|---|---|---|
| `table_name` | STRING | Exported table name = the Pub/Sub message `table` and the Dataform action that triggers the export (e.g. dim_company). Key of the table. |
| `source_view` | STRING | Full name of the export view in dataset pub_sub (databuffet-nonprd.pub_sub.export_<table>), resolved by ref() at compile time. |
| `topic` | STRING | Pub/Sub topic the changed rows are published to. |
| `last_invocation_id` | STRING | Workflow memory: id (after workflowInvocations/) of the last Dataform workflow invocation already handled for this table. |
| `last_invocation_end` | TIMESTAMP | End time (UTC) of that invocation; NULL before the first export; only invocations that ended later count as new. |
| `claimed_at` | TIMESTAMP | Shared being-processed marker (UTC) set by the publisher or the first-load exporter; NULL = free; older than 30 minutes = abandoned and may be re-claimed. |

# How it is built

- Definition: `definitions/process/mart_export_config.sqlx` (`type: "operations"`, tags `pub_sub`); the operation owns this table.
- Reads: [pub_sub.export_dim_company](/view/pub_sub/export_dim_company.md).
- Operations (`type: "operations"`, tag `pub_sub`, no scheduler runs it; deployed manually from the `production` release config with dependencies off after the code reaches nonprod). `CREATE TABLE IF NOT EXISTS`, then an insert-only MERGE from the JSON config, so re-runs preserve every existing row including the workflow's memory. `ref()` to each export view makes a config row naming a missing view a compile error.
- Approximate size (BigQuery metadata, 2026-10-31): 1 rows, 139 B.

# Examples

Export state and whether a run holds the claim.

```sql
SELECT table_name, source_view, topic, last_invocation_id,
       last_invocation_end, claimed_at,
       claimed_at IS NOT NULL AND claimed_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 MINUTE) AS is_claimed
FROM `databuffet-nonprd.process_dataset.mart_export_config`
```

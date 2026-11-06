---
type: BigQuery View
title: "export_dim_aging_rang"
description: "One row = one aging range (day band) of the receivables aging report, exposed for the Pub/Sub export of dimension_table.dim_aging_rang with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_aging_rang&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_aging_rang
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_aging_rang.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_aging_rang.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_aging_rang](/dimension/dim_aging_rang.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_aging_rang`.

# Grain and key

One row = one aging range (day band) of the receivables aging report: key `AgingRangSK` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingRangSK` | INT64 | Stable surrogate key of the bucket. Assigned once (MERGE with `max_sk`) and never regenerated. |
| `ReportName` | STRING | Display label of the bucket as shown on aging reports (MDS `ReportName`). |
| `AgingDayMin` | INT64 | Lower bound of the bucket in days past due (inclusive; cast to INT64 from MDS). Used as `DayRange BETWEEN AgingDayMin AND AgingDayMax`. |
| `AgingDayMax` | INT64 | Upper bound of the bucket in days past due (inclusive; cast to INT64 from MDS). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_aging_rang.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_aging_rang](/dimension/dim_aging_rang.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_aging_rang`
GROUP BY row_key
HAVING n > 1
```

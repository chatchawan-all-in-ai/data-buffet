---
type: BigQuery View
title: "export_dim_product_series"
description: "One row = one product series, exposed for the Pub/Sub export of dimension_table.dim_product_series with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_product_series&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_product_series
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_product_series.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_product_series.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_product_series](/dimension/dim_product_series.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_product_series`.

# Grain and key

One row = one product series: key `SeriesCode` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `SeriesCode` | STRING | Series code (mds `SeriesCode`, trimmed, empty to NULL); unique key. |
| `SeriesName` | STRING | Series name (mds `SeriesName`, trimmed, empty to NULL). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_product_series.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_product_series](/dimension/dim_product_series.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_product_series`
GROUP BY row_key
HAVING n > 1
```

---
type: BigQuery View
title: "export_dim_pump_information"
description: "One row = one pump segment per company, product code, region and new-product flag, exposed for the Pub/Sub export of dimension_table.dim_pump_information with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_pump_information&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_pump_information
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_pump_information.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_pump_information.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:27:50+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_pump_information](/dimension/dim_pump_information.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_pump_information`.

# Grain and key

One row = one pump segment per company, product code, region and new-product flag: key `CompanyID`, `milstk`, `RegionID`, `FlagNewProductMKT` (unique); `row_key` is the JSON of that key. `CompanyID`, `milstk`, `RegionID`, `FlagNewProductMKT` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `PumpSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by lower(milstk), RegionID, FlagNewProductMKT. Regenerated every run. |
| `PumpSegment` | STRING | Pump segment: `dim_product_mkt.Segment` when RegionID is 'PS1' and FlagNewProductMKT is true, otherwise `view_dim_product_master.PumpSegment`. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_pump_information.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_pump_information](/dimension/dim_pump_information.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_pump_information`
GROUP BY row_key
HAVING n > 1
```

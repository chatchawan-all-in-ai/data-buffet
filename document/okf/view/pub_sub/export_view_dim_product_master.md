---
type: BigQuery View
title: "export_view_dim_product_master"
description: "One row = one product, exposed for the Pub/Sub export of dimension_view.view_dim_product_master with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_product_master&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_product_master
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_product_master.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_product_master.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_product_master](/view/dimension_view/view_dim_product_master.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_product_master`.

# Grain and key

One row = one product: key `ProductSK` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductSK` | INT64 | SK of the product in dim_product_master (MERGE). |
| `ProductCode` | STRING | MAC5 stock code (`stkcode`). |
| `ProductCode1` | STRING | Secondary product code or short model name. |
| `ProductName` | STRING | Full product name. |
| `ProductDescription` | STRING | Product name/description. |
| `ProductMac5Description` | STRING | MAC5 stock description (`stkdesct1`). |
| `PumpSegment` | STRING | Pump segment label: for SegmentID 00111/00112 the WaterPac name, taken as the first non-NULL of the dim_waterpac names matched by the WaterPac code of `ProductCode`, `ProductCode1`, `ProductMac5Description` (in that order), else 'WaterPac'; the marketing Segment for MarketingGroupID 002; else 'OTHERS'. The WaterPac code is the text after `/` that starts with P or U (regex `/([PU][a-zA-Z0-9].*)$`). |
| `BrandID` | STRING | Brand of the product (FK to `brand.bra_id`). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_product_master.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_product_master](/view/dimension_view/view_dim_product_master.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_product_master`
GROUP BY row_key
HAVING n > 1
```

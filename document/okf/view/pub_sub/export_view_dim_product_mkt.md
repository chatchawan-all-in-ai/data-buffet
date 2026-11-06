---
type: BigQuery View
title: "export_view_dim_product_mkt"
description: "One row = one marketing group, sub group, segment and type combination of a company, exposed for the Pub/Sub export of dimension_view.view_dim_product_mkt with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_product_mkt&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_product_mkt
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_product_mkt.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_product_mkt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-view_dim_product_mkt`.

# Grain and key

One row = one marketing group, sub group, segment and type combination of a company: key `CompanyID`, `MarketingGroupID`, `SubMarketingID`, `SegmentID`, `TypeMarketingID` (unique); `row_key` is the JSON of that key. `CompanyID` is a column of the source table that is not exported as a data column; it appears only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMktSK` | INT64 | SK of the marketing classification in dim_product_mkt (regenerated daily). |
| `MarketingGroupID` | STRING | Marketing group code (level 2). |
| `MarketingGroup` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing code (level 3). |
| `SubMarketing` | STRING | Sub-marketing name. |
| `SegmentID` | STRING | Segment code (level 4). |
| `Segment` | STRING | Segment name. |
| `TypeMarketing` | STRING | Marketing type name. |
| `TypeMarketingID` | STRING | Marketing type code (top level). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_product_mkt.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_product_mkt`
GROUP BY row_key
HAVING n > 1
```

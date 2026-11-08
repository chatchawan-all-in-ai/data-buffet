---
type: BigQuery View
title: "export_dim_customer_segment"
description: "One row = one customer segment, exposed for the Pub/Sub export of dimension_table.dim_customer_segment with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_customer_segment&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_customer_segment
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_customer_segment.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_customer_segment.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_customer_segment](/dimension/dim_customer_segment.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_customer_segment`.

# Grain and key

One row = one customer segment: key `CompanyID`, `Segment3` (unique); `row_key` is the JSON of that key. `CompanyID` is a column of the source table that is not exported as a data column; it appears only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerSegmentSK` | INT64 | Stable surrogate key for the active `companyID`, `Segment3` natural key; the fixed value `-1` is reserved for the 'Non-Segment' fallback row. |
| `Segment1` | STRING | Pass-through of mds `Segment1`, cleaned with `cleanString` (empty string becomes NULL). Top level of the three-level segment code; 'Non-Segment' on the -1 row. |
| `Segment2` | STRING | Pass-through of mds `Segment2`, cleaned with `cleanString` (empty string becomes NULL). Middle segment level; 'Non-Segment' on the -1 row. |
| `Segment3` | STRING | Pass-through of mds `Segment3`, cleaned with `cleanString` (empty string becomes NULL). Leaf segment level (the row key together with company); 'Non-Segment' on the -1 row. |
| `DescriptionThai` | STRING | Pass-through of mds `DescriptionThai`, cleaned with `cleanString` (empty string becomes NULL). Thai description of the segment. |
| `DescriptionEng` | STRING | Pass-through of mds `DescriptionEng`, cleaned with `cleanString` (empty string becomes NULL). English description of the segment. |
| `SortOrder` | INT64 | Display sort order (`castInt64` of mds `SortOrder`); the -1 row uses 99 so it sorts last. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_customer_segment.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_customer_segment](/dimension/dim_customer_segment.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_customer_segment`
GROUP BY row_key
HAVING n > 1
```

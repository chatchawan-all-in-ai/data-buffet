---
type: BigQuery Table
title: "dim_zone_mdt"
description: "One row = one MDT sales zone (ZoneCode) with its name and validity dates, from the MDS MDT zone master, plus a reserved -1 NotZone row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_zone_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_zone_mdt
tags: ["dimension", "mds", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_zone_mdt.sqlx"
    title: "Dataform definition (dimension/dim_zone_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Zone master for the MDT (modern-trade) saleout side. `dim_sales_branch_mdt` joins it on ZoneCode to put each branch into a zone, and `dim_zone_ta_mdt` joins it to attach zone managers.

Read by: [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md), [dim_zone_ta_mdt](/dimension/dim_zone_ta_mdt.md).

# Grain and key

One row = one MDT sales zone: key trimmed `zone_id` (`ZoneCode`); duplicates are collapsed keeping the row with the latest start_date (ties by id). `ZoneMdtSK` is `ROW_NUMBER()` ordered by ZoneCode. Reserved row `ZoneMdtSK = -1` with ZoneCode 'NotZone', ZoneName 'ไม่ระบุโซน' and NULL dates/MdsID.

# Schema

| Column | Type | Description |
|---|---|---|
| `ZoneMdtSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by ZoneCode; -1 for the NotZone row. Regenerated every run. |
| `ZoneCode` | STRING | Zone code (`zone_id` trimmed, empty becomes NULL); 'NotZone' on the -1 row. Join key used by dim_sales_branch_mdt and dim_zone_ta_mdt. |
| `ZoneName` | STRING | Zone name; 'ไม่ระบุโซน' on the -1 row. |
| `StartDate` | DATE | MDS start_date of the kept row; NULL on the -1 row. |
| `EndDate` | DATE | MDS end_date of the kept row; NULL on the -1 row. |
| `MdsID` | STRING | `id` of the source row in `mds_data_mdt_sales_zone_master`; trace column back to MDS. NULL on the -1 row. |

# How it is built

- Definition: `definitions/dimension/dim_zone_mdt.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `ZoneMdtSK`.
- Storage options: `{"clusterBy": ["ZoneMdtSK"]}`.
- Reads: `mds_dataset.mds_data_mdt_sales_zone_master` (master data loaded outside this repo).
- Full daily rebuild (`type: "table"`, tags `dimension_daily`, `saleout_daily`); no declared dependencies.

# Examples

All MDT zones including the reserved row.

```sql
SELECT ZoneMdtSK, ZoneCode, ZoneName
FROM `databuffet-nonprd.dimension_table.dim_zone_mdt`
ORDER BY ZoneMdtSK;
```

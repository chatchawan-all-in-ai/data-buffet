---
type: BigQuery Table
title: "dim_zone_ta_mdt"
description: "One row = one zone manager (TA) assignment for an MDT zone over one StartDate to EndDate interval, from the MDS zone manager master, plus a reserved -1 row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_zone_ta_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_zone_ta_mdt
tags: ["dimension", "mds", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_zone_ta_mdt.sqlx"
    title: "Dataform definition (dimension/dim_zone_ta_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Says which employee is the zone manager of each MDT zone. `dim_sales_branch_mdt` joins it on ZoneCode to give every branch a `ZoneTaMdtSK`.

Read by: [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md).

# Grain and key

One row = one active MDS zone manager assignment (no de-duplication): key `ZoneTaMdtSK`, `ROW_NUMBER()` ordered by zone_id then employee id. A zone can have several rows (several managers or intervals); `dim_sales_branch_mdt` keeps the lowest ZoneTaMdtSK per ZoneCode. Reserved row `ZoneTaMdtSK = -1` with ZoneMdtSK -1, ZoneCode 'NotZone', EmployeeID 'NotEmployee', EmployeeName 'ไม่ระบุผู้จัดการโซน'.

# Schema

| Column | Type | Description |
|---|---|---|
| `ZoneTaMdtSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by ZoneCode and employee id; -1 for the reserved row. Regenerated every run. |
| `ZoneMdtSK` | INT64 | SK of the zone in [dim_zone_mdt](/dimension/dim_zone_mdt.md) (join on ZoneCode); -1 when the zone code is not in dim_zone_mdt. |
| `ZoneCode` | STRING | Zone code (`zone_id` trimmed); 'NotZone' on the -1 row. |
| `ZoneName` | STRING | Zone name as entered in the manager master; 'ไม่ระบุโซน' on the -1 row. |
| `EmployeeID` | STRING | Employee code of the zone manager as a string (source FLOAT64 cast to INT64 then STRING to drop '.0'); 'NotEmployee' on the -1 row. |
| `EmployeeName` | STRING | Manager given name; 'ไม่ระบุผู้จัดการโซน' on the -1 row. |
| `EmployeeSurname` | STRING | Manager surname. |
| `EmployeeNickname` | STRING | Manager nickname. |
| `StartDate` | DATE | MDS start_date of the assignment; NULL on the -1 row. |
| `EndDate` | DATE | MDS end_date of the assignment; NULL on the -1 row. |
| `MdsID` | STRING | `id` of the source row in `mds_data_mdt_sales_zone_ta_master`; trace column back to MDS. NULL on the -1 row. |

# How it is built

- Definition: `definitions/dimension/dim_zone_ta_mdt.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `ZoneTaMdtSK`.
- Storage options: `{"clusterBy": ["ZoneTaMdtSK"]}`.
- Reads: `mds_dataset.mds_data_mdt_sales_zone_ta_master` (master data loaded outside this repo), [dimension_table.dim_zone_mdt](/dimension/dim_zone_mdt.md).
- Full daily rebuild (`type: "table"`, tags `dimension_daily`, `saleout_daily`); runs after dim_zone_mdt.

# Examples

Zone managers per zone (excluding the reserved row).

```sql
SELECT ZoneCode, ZoneName, EmployeeID, StartDate, EndDate
FROM `databuffet-nonprd.dimension_table.dim_zone_ta_mdt`
WHERE ZoneTaMdtSK <> -1
ORDER BY ZoneCode, StartDate;
```

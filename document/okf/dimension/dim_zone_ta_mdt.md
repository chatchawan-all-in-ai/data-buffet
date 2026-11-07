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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Says which employee is the zone manager of each MDT zone. `dim_sales_branch_mdt` joins it on ZoneCode to give every branch a `ZoneTaMdtSK`.

Read by: [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md).

# Grain and key

One row = one active MDS zone manager assignment (no de-duplication). Natural key: (`ZoneCode`, `EmployeeID`, `StartDate`, `EndDate`). `ZoneTaMdtSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `ZoneTaMdtSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `ZoneMdtSK` | INT64 | SK of the zone in [dim_zone_mdt](/dimension/dim_zone_mdt.md) (join on ZoneCode); -1 when the zone code is not in dim_zone_mdt. |
| `ZoneCode` | STRING | Zone code (`zone_id` trimmed); 'NotZone' on the -1 row. |
| `ZoneName` | STRING | Zone name as entered in the manager master; 'ไม่ระบุโซน' on the -1 row. |
| `EmployeeID` | STRING | Employee code of the zone manager as a string (source FLOAT64 cast to INT64 then STRING to drop '.0'); 'NotEmployee' on the -1 row. |
| `EmployeeName` | STRING | Manager given name; 'ไม่ระบุผู้จัดการโซน' on the -1 row. |
| `EmployeeSurname` | STRING | Manager surname. |
| `EmployeeNickname` | STRING | Manager nickname. |
| `StartDate` | DATE | MDS start_date of the assignment; NULL on the -1 row. |
| `EndDate` | DATE | MDS end_date of the assignment; NULL on the -1 row. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_mdt_sales_zone_ta_master`; trace column back to MDS. NULL on the -1 row. |
# How it is built

- Definition: `definitions/dimension/dim_zone_ta_mdt.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`, `saleout_daily`).
- Reads: `mds_dataset.mds_data_mdt_sales_zone_ta_master` (master data loaded outside this repo), [dimension_table.dim_zone_mdt](/dimension/dim_zone_mdt.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_zone_mdt.
# Examples

Zone managers per zone (excluding the reserved row).

```sql
SELECT ZoneCode, ZoneName, EmployeeID, StartDate, EndDate
FROM `databuffet-nonprd.dimension_table.dim_zone_ta_mdt`
WHERE ZoneTaMdtSK <> -1
ORDER BY ZoneCode, StartDate;
```

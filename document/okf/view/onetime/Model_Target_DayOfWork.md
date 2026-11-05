---
type: BigQuery View
title: "Model_Target_DayOfWork"
description: "One row = one day-of-work target for CompanySK 4, with org (latest structure), marketing and report names."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=onetime&t=Model_Target_DayOfWork&page=table"
project_id: databuffet-nonprd
dataset_id: onetime
table_id: Model_Target_DayOfWork
tags: ["view", "onetime"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/onetime/Model_Target_DayOfWork.sqlx"
    title: "Dataform definition (view/onetime/Model_Target_DayOfWork.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The target side of the sales model, the counterpart of [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md). It flattens [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md) (monthly targets spread over working days, 0 on holidays) into readable columns: sales rep, team, section, region, director, marketing group/segment, channel target group and report line. The org columns are resolved from the `*_last` dimensions by joining the SKs stored on the target row.

No other object in this repo reads it.

# Grain and key

One row = one day-of-work target row of `dim_target_product_group_by_sale_dayofwork` with `CompanySK = 4`: key `TargetBySaleDayofworkSK` (unique in the source dimension). Every join is a LEFT JOIN on SK + `CompanySK` to the `*_last` dims, `dim_product_mkt`, `dim_target_product_group` and `dim_report`, each matching one row per SK, so the row count equals the source rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetBySaleDayofworkSK` | INT64 | Row key of `dim_target_product_group_by_sale_dayofwork` (one target day for a sales person/department + marketing group). Same column as in `Model_Invoice_Transaction`. |
| `TargetDate` | DATE | Calendar date built from `Year`, `Month` and `Day` of the target row. |
| `TargetYear` | INT64 | Year of the target. |
| `TargetMonth` | INT64 | Month of the target. |
| `TargetDay` | STRING | Day of month of the target (STRING in the source dimension). |
| `SalesRepID` | STRING | Employee id from dim_sale_representative_last via the source SaleRepSK. |
| `SalesRepNameSurname` | STRING | Name from that sales-representative match. |
| `TeamID` | STRING | Department/team id from that sales-representative match. |
| `TeamName` | STRING | Department name resolved through that sales-representative match in dim_department_last. |
| `SectionID` | STRING | Section id from dim_section_last via the source SectionSK. |
| `SectionName` | STRING | Name from that section match. |
| `SectionManagerNameSurname` | STRING | Name from dim_section_manager_last via the source SectionManagerSK. |
| `RegionID` | STRING | Region id from dim_region_last via the source RegionSK. |
| `RegionName` | STRING | Name from that region match. |
| `RegionManagerNameSurname` | STRING | Name from dim_region_manager_last via the source RegionManagerSK. |
| `DirectorID` | STRING | Director id from dim_director_last via the source DirectorSK. |
| `DirectorName` | STRING | Name/group label from that director match. |
| `DirectorSalesNameSurname` | STRING | DirectorOfSalesName from that director match. |
| `MarketingGroupID` | STRING | Marketing group id from `dim_product_mkt` (via ProductMktSK). |
| `MarketingGroupName` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing group id. |
| `SubMarketingName` | STRING | Sub-marketing group name. |
| `SegmentID` | STRING | Segment id. |
| `SegmentName` | STRING | Segment name. |
| `ChannelTargetGroup` | STRING | Target channel group of the target (e.g. `MDT` is one value; the code list is in `dim_target_product_group`). |
| `TargetAmount` | FLOAT64 | Daily target amount (`Amt_New`): monthly amount divided by the working days of the month, 0 on holidays. |
| `TargetQuantity` | FLOAT64 | Daily target quantity (`Qty_New`), computed the same way. |
| `ReportID` | STRING | Report line id from `dim_report`. |
| `ReportName1` | STRING | Report name level 1. |
| `ReportName2` | STRING | Report name level 2. |

# How it is built

- Definition: `definitions/view/onetime/Model_Target_DayOfWork.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_target_product_group](/dimension/dim_target_product_group.md), [dimension_table.dim_report](/dimension/dim_report.md).

# Examples

Monthly target amount by region and marketing group.

```sql
SELECT TargetYear, TargetMonth, RegionID, MarketingGroupName,
       SUM(TargetAmount) AS target_amount, SUM(TargetQuantity) AS target_qty
FROM `databuffet-nonprd.onetime.Model_Target_DayOfWork`
GROUP BY TargetYear, TargetMonth, RegionID, MarketingGroupName
ORDER BY TargetYear, TargetMonth, RegionID
```

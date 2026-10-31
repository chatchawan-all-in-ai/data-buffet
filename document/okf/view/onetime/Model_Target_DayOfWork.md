---
type: BigQuery View
title: "Model_Target_DayOfWork"
description: "One row = one day-of-work target for CompanySK 4, with marketing/report names and potentially incorrect org attributes due to joins across independently numbered dimension families."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The target side of the sales BI model, the counterpart of [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md). It flattens [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md) (monthly targets spread over working days, 0 on holidays) into readable columns: sales rep, team, section, region, director, marketing group/segment, channel target group and report line. It joins date-aware target SKs to independently numbered latest-org dimensions.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per row of `dim_target_product_group_by_sale_dayofwork` with `CompanySK = 4` (hard-coded): one row per target date x sales rep/department x marketing group/sub/segment (key `TargetBySaleDayofworkSK`). Joins to the `*_last` dims and `dim_target_product_group`, `dim_product_mkt`, `dim_report` are LEFT JOINs intended to be 1:1.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetBySaleDayofworkSK` | INT64 | Row key of `dim_target_product_group_by_sale_dayofwork` (one target day for a sales person/department + marketing group); regenerated daily. Same column as in `Model_Invoice_Transaction`. |
| `TargetDate` | DATE | Calendar date built from `Year`, `Month` and `Day` of the target row. |
| `TargetYear` | INT64 | Year of the target. |
| `TargetMonth` | INT64 | Month of the target. |
| `TargetDay` | STRING | Day of month of the target (STRING in the source dimension). |
| `SalesRepID` | STRING | Employee id from dim_sale_representative_last via the source SaleRepSK; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `SalesRepNameSurname` | STRING | Name from that sales-representative match (personal data); potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `TeamID` | STRING | Department/team id from that sales-representative match; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `TeamName` | STRING | Department name resolved through that sales-representative match in dim_department_last; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `SectionID` | STRING | Section id from dim_section_last via the source SectionSK; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `SectionName` | STRING | Name from that section match; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `SectionManagerNameSurname` | STRING | Name from dim_section_manager_last via the source SectionManagerSK (personal data); potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `RegionID` | STRING | Region id from dim_region_last via the source RegionSK; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `RegionName` | STRING | Name from that region match; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `RegionManagerNameSurname` | STRING | Name from dim_region_manager_last via the source RegionManagerSK (personal data); potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `DirectorID` | STRING | Director id from dim_director_last via the source DirectorSK; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `DirectorName` | STRING | Name/group label from that director match; potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
| `DirectorSalesNameSurname` | STRING | DirectorOfSalesName from that director match (personal data); potentially incorrect or unmatched because date-aware SKs are joined to latest-org dimensions. |
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
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `dim_target_product_group_by_sale_dayofwork` (tag `dimension_daily`) and the `*_last` org dims, `dim_product_mkt`, `dim_target_product_group` and `dim_report`.

# Examples

Monthly target amount by date-aware region and marketing group, resolving the source table's RegionSK against dim_region.

```sql
SELECT t.Year AS TargetYear, t.Month AS TargetMonth, r.RegionID, t.MarketingGroupName,
       SUM(t.Amt_New) AS target_amount, SUM(t.Qty_New) AS target_qty
FROM `databuffet-nonprd.dimension_table.dim_target_product_group_by_sale_dayofwork` AS t
LEFT JOIN `databuffet-nonprd.dimension_table.dim_region` AS r
  ON t.RegionSK = r.RegionSK AND t.CompanySK = r.CompanySK
WHERE t.CompanySK = 4
GROUP BY t.Year, t.Month, r.RegionID, t.MarketingGroupName
ORDER BY TargetYear, TargetMonth, r.RegionID
```

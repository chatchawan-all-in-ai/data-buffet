---
type: BigQuery Table
title: "dim_target_product_group_by_sale_dayofwork"
description: "One row = one allocated target row of dim_target_product_group_by_sale spread onto one calendar date (Amt_New and Qty_New for that date, zero on holidays), with the org-hierarchy SKs valid on that date."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_target_product_group_by_sale_dayofwork&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_target_product_group_by_sale_dayofwork
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_target_product_group_by_sale_dayofwork.sqlx"
    title: "Dataform definition (dimension/dim_target_product_group_by_sale_dayofwork.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Daily (day-of-work) version of the per-employee target: the monthly CalAmt / CalQty are divided by the number of non-holiday days of the month and assigned to each date, so a daily target can be compared with daily sales. `fact_transcation` carries its `TargetBySaleDayofworkSK`, so facts and daily targets can be reported together.

Read by: [export_dim_target_product_group_by_sale_dayofwork](/view/pub_sub/export_dim_target_product_group_by_sale_dayofwork.md), [fact_transcation](/fact/fact_transcation.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [view_fact_target_product_group_mdt](/view/fact_view/view_fact_target_product_group_mdt.md).

# Grain and key

One row = one allocated target row on one calendar date: key (`TargetBySaleSK`, `Date`) after the DISTINCT (dates come from `dim_calendar` for the target year and month, limited to StartDate..EndDate of the rate rule when set). The date-valid SKs (SaleRepSK, DepartmentSK, RegionSK, RegionManagerSK, DirectorSK, SectionSK, SectionManagerSK) are resolved by natural keys and `Date BETWEEN StartDate AND EndDate` against the non-`_last` dims, while the `*Last` columns are carried from dim_target_product_group_by_sale. Special rows: when dim_rate_target has a dated rule for the same company, year, month, employee and department, only those dated rows are kept for that employee-month (the others are dropped). SK `TargetBySaleDayofworkSK` = `ROW_NUMBER()` over Year, Month, Day, TargetBySaleSK.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetBySaleDayofworkSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by Year, Month, Day, TargetBySaleSK. Regenerated every run. |
| `SaleRepSK` | INT64 | SK in [dim_sale_representative](/dimension/dim_sale_representative.md) valid on `Date` (EmployeeID + DepartmentID + CompanySK); falls back to the employee's row with DepartmentID NULL; NULL if none. |
| `DepartmentSK` | INT64 | SK in dim_department valid on Date (DepartmentID + CompanySK). |
| `RegionSK` | INT64 | SK in [dim_region](/dimension/dim_region.md) valid on Date, matched through the department (RegionID, and SubRegionID = SectionID when region and sub-region differ). |
| `RegionManagerSK` | INT64 | SK in [dim_region_manager](/dimension/dim_region_manager.md) valid on Date for that region and sub-region. |
| `DirectorSK` | INT64 | SK in dim_director valid on Date, via the region's DirectorID. |
| `SectionSK` | INT64 | SK in [dim_section](/dimension/dim_section.md) valid on Date for the department's SectionID. |
| `SectionManagerSK` | INT64 | SK in [dim_section_manager](/dimension/dim_section_manager.md) valid on Date for that section. |
| `Date` | DATE | Calendar date (from dim_calendar) the daily target belongs to; can be NULL when no calendar day matched the rule's date range. |
| `TargetBySaleSK` | INT64 | SK of the source row in [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md) (same-day numbering). |
| `SaleRepSKLast` | INT64 | Copied from dim_target_product_group_by_sale: latest-snapshot sales rep SK (dim_sale_representative_last). |
| `DepartmentSKLast` | INT64 | Copied: latest department SK (dim_department_last). |
| `RegionSKLast` | INT64 | Copied: latest region SK (dim_region_last). |
| `RegionManagerSKLast` | INT64 | Copied: latest region manager SK (dim_region_manager_last). |
| `SectionSKLast` | INT64 | Copied: latest section SK (dim_section_last). |
| `SectionManagerSKLast` | INT64 | Copied: latest section manager SK (dim_section_manager_last). |
| `DirectorSKLast` | INT64 | Copied: latest director SK (dim_director_last). |
| `ReportSK` | INT64 | Copied from the by-sale table: SK in dim_report. |
| `TargetProductGroupSK` | INT64 | Copied: SK of the source target in dim_target_product_group. |
| `RateTargetSK` | INT64 | Copied: SK of the rate rule in dim_rate_target; NULL for an unmatched allocation branch, which can coexist with matched rows for the target. |
| `ProductMktSK` | INT64 | Copied: SK in dim_product_mkt. |
| `CompanySK` | INT64 | Copied from [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md).CompanySK. |
| `companyID` | STRING | Copied: company code. |
| `Year` | INT64 | Copied: target year (also the join key to the calendar). |
| `Month` | INT64 | Copied: target month. |
| `MarketingGroupID` | STRING | Copied: marketing group code. |
| `MarketingGroupName` | STRING | Copied: marketing group name. |
| `SubMarketingID` | STRING | Copied: sub group code. |
| `SubMarketingName` | STRING | Copied: sub group name. |
| `SegmentID` | STRING | Copied: segment code. |
| `SegmentName` | STRING | Copied: segment name. |
| `ChannelTargetGroup` | STRING | Copied: channel group of the target. |
| `TargetID` | STRING | Copied: target code. |
| `Amt` | FLOAT64 | Copied: the whole (unallocated) target amount of the month; repeated on every day row. |
| `Qty` | FLOAT64 | Copied: the whole target quantity of the month; repeated on every day row. |
| `EmployeeID` | STRING | Copied: employee receiving the share. |
| `Percent` | FLOAT64 | Copied: share in percent. |
| `DepartmentID` | STRING | Copied: employee department. |
| `StartDate` | DATE | Copied: start date of the rate rule; NULL means the rule covers the whole month. |
| `EndDate` | DATE | Copied: end date of the rate rule. |
| `CalAmt` | FLOAT64 | Copied: monthly allocated amount = Amt * Percent / 100 (the amount that Amt_New divides). |
| `CalQty` | FLOAT64 | Copied: monthly allocated quantity. |
| `Day` | STRING | Day of month from dim_calendar (STRING). |
| `total_day` | INT64 | Number of non-holiday days (`HolidayFlag = 'No'`) of the whole Year and month in dim_calendar; the divisor of the daily target. |
| `Amt_New` | FLOAT64 | Daily target amount = CalAmt / total_day truncated to 10 decimals; 0 on holidays (`HolidayFlag = 'Yes'`). The column to sum for daily targets. |
| `Qty_New` | FLOAT64 | Daily target quantity = CalQty / total_day truncated to 10 decimals; 0 on holidays. |

# How it is built

- Definition: `definitions/dimension/dim_target_product_group_by_sale_dayofwork.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `TargetBySaleDayofworkSK`.
- Storage options: `{"clusterBy": ["TargetBySaleDayofworkSK"]}`.
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md), [dimension_table.dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_department](/dimension/dim_department.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_section_manager](/dimension/dim_section_manager.md), [dimension_table.dim_rate_target](/dimension/dim_rate_target.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_calendar, dim_rate_target, dim_target_product_group_by_sale and the non-`_last` dims dim_sale_representative, dim_department, dim_director, dim_region, dim_region_manager, dim_section and dim_section_manager.

# Examples

Daily target for one employee in the current month.

```sql
SELECT Date, EmployeeID, DepartmentID, MarketingGroupID, SUM(Amt_New) AS day_target_amt, SUM(Qty_New) AS day_target_qty
FROM `databuffet-nonprd.dimension_table.dim_target_product_group_by_sale_dayofwork`
WHERE Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
  AND Month = EXTRACT(MONTH FROM CURRENT_DATE('Asia/Bangkok'))
  AND companyID = 'ag01'
GROUP BY 1, 2, 3, 4
ORDER BY Date, EmployeeID
LIMIT 200;
```

Monthly total per company to compare against the by-sale table.

```sql
SELECT companyID, Year, Month, SUM(Amt_New) AS day_sum_amt
FROM `databuffet-nonprd.dimension_table.dim_target_product_group_by_sale_dayofwork`
WHERE Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
```

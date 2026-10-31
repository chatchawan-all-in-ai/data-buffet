---
type: BigQuery View
title: "view_dim_target_by_agent_dayofwork"
description: "One row = one allocated sales target spread to one calendar date (working days only get a share), with the as-of-date org SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_target_by_agent_dayofwork&page=table"
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_target_by_agent_dayofwork.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_target_by_agent_dayofwork.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily spread of the by-agent targets: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md) (monthly allocation per agent) is joined to the calendar so that `CalAmt`/`CalQty` are divided evenly over the month's working days (`Amt_New`/`Qty_New`; holidays get 0). It also resolves the as-of-date org SKs (sales rep, department, region, section, managers, director) from the date-versioned dims using StartDate/EndDate. Nothing else in the repo reads it.

# Grain and key

One row per TargetBySaleSK x Date of the target month (`TargetBySaleDayofworkSK` is a generated ROW_NUMBER over Year, Month, Day, TargetBySaleSK). `SELECT DISTINCT` guards against join fan-out.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetBySaleDayofworkSK` | INT64 | Generated ROW_NUMBER over Year, Month, Day, TargetBySaleSK (changes every run). |
| `SaleRepSK` | INT64 | As-of-date SK of the sales representative (Date within StartDate-EndDate, by EmployeeID + DepartmentID + CompanySK); falls back to the employee's NULL-department row. |
| `DepartmentSK` | INT64 | As-of-date SK of the department in dim_department. |
| `RegionSK` | INT64 | As-of-date SK of the region in dim_region (RegionID/SubRegionID rules apply). |
| `RegionManagerSK` | INT64 | As-of-date SK of the region manager in dim_region_manager. |
| `DirectorSK` | INT64 | As-of-date SK of the director in dim_director. |
| `SectionSK` | INT64 | As-of-date SK of the section in dim_section. |
| `SectionManagerSK` | INT64 | As-of-date SK of the section manager in dim_section_manager. |
| `Date` | DATE | Calendar date within the target month (from dim_calendar). |
| `TargetBySaleSK` | INT64 | SK of the monthly target-by-sale row in dim_target_product_group_by_sale (regenerated daily). |
| `SaleRepSKLast` | INT64 | SK of the target owner in dim_sale_representative_last, matched by EmployeeID + DepartmentID + CompanySK; for owners with no department match falls back to the row with NULL DepartmentID for the same employee. |
| `DepartmentSKLast` | INT64 | SK of the owner's department in dim_department_last. |
| `RegionSKLast` | INT64 | SK of the owner's region in dim_region_last. |
| `RegionManagerSKLast` | INT64 | SK of the region manager in dim_region_manager_last. |
| `SectionSKLast` | INT64 | SK of the owner's section in dim_section_last. |
| `SectionManagerSKLast` | INT64 | SK of the section manager in dim_section_manager_last. |
| `DirectorSKLast` | INT64 | SK of the director in dim_director_last (through the region). |
| `ReportSK` | INT64 | SK of the report row in dim_report chosen by region (and marketing group when the region has several report rows); NULL when none. |
| `TargetProductGroupSK` | INT64 | SK of the target row in dim_target_product_group. |
| `RateTargetSK` | INT64 | SK of the allocation-rate row in dim_rate_target; NULL for an unmatched allocation branch, which can coexist with matched rows for the target. |
| `ProductMktSK` | INT64 | SK of the marketing classification in dim_product_mkt matched on group/sub/segment IDs + CompanySK. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `Year` | INT64 | Target year. |
| `Month` | INT64 | Target month (1-12). |
| `MarketingGroupID` | STRING | Marketing group code of the target (dim_target_product_group). |
| `MarketingGroupName` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing code. |
| `SubMarketingName` | STRING | Sub-marketing name. |
| `SegmentID` | STRING | Segment code. |
| `SegmentName` | STRING | Segment name. |
| `ChannelTargetGroup` | STRING | Channel target group of the target (MDS). |
| `TargetID` | STRING | Target code (joins targets to allocation rates in dim_rate_target). |
| `Amt` | FLOAT64 | Target amount (THB) of the whole target row before allocation. |
| `Qty` | FLOAT64 | Target quantity of the whole target row before allocation. |
| `EmployeeID` | STRING | Employee (salesperson) who receives the allocation, from dim_rate_target. |
| `Percent` | FLOAT64 | Allocation percentage for this employee (0-100) from dim_rate_target. |
| `DepartmentID` | STRING | Department of the employee in the rate row. |
| `CalAmt` | FLOAT64 | Allocated target amount = Amt x Percent / 100. |
| `CalQty` | FLOAT64 | Allocated target quantity for the month (Qty x Percent / 100). |
| `Day` | STRING | Two-digit day of month as text (dim_calendar `Day`). |
| `total_day` | INT64 | Number of distinct working days in the target's year-month (HolidayFlag = 'No'). |
| `Amt_New` | FLOAT64 | Daily target amount: TRUNC(CalAmt / total_day, 10) on working days, 0 on holidays. |
| `Qty_New` | FLOAT64 | Daily target quantity: TRUNC(CalQty / total_day, 10) on working days, 0 on holidays. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_target_by_agent_dayofwork.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md), [dimension_table.dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_department](/dimension/dim_department.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_section_manager](/dimension/dim_section_manager.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_calendar, dim_target_product_group_by_sale and the date-versioned dims (dim_sale_representative, dim_department, dim_region, dim_director, dim_section, dim_region_manager, dim_section_manager). All upstream tables are daily full rebuilds (`dimension_daily`).

# Examples

Daily target for a salesperson in one month:

```sql
SELECT Date, SUM(Amt_New) AS daily_target
FROM `databuffet-nonprd.dimension_view.view_dim_target_by_agent_dayofwork`
WHERE companyID = 'ag01' AND Year = 2026 AND Month = 10 AND EmployeeID = 'E001'
GROUP BY Date
ORDER BY Date
```

Month total after daily spread:

```sql
SELECT Year, Month, SUM(Amt_New) AS spread_amt
FROM `databuffet-nonprd.dimension_view.view_dim_target_by_agent_dayofwork`
WHERE Year = 2026
GROUP BY Year, Month
ORDER BY Month
```

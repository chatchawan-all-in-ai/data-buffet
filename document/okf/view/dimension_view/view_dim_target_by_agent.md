---
type: BigQuery View
title: "view_dim_target_by_agent"
description: "One row = one sales target (product group, year, month, target ID) allocated to one salesperson, with the latest org-chart SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_target_by_agent&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_target_by_agent
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_target_by_agent.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_target_by_agent.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Sales target allocation by agent: each monthly product-group target from [dim_target_product_group](/dimension/dim_target_product_group.md) is split to salespeople using [dim_rate_target](/dimension/dim_rate_target.md) percentages (CalAmt/CalQty), and tagged with the owner's latest department/section/region/director SKs from the `_last` dims and a ReportSK from [dim_report](/dimension/dim_report.md). The daily-spread counterpart is [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), which reads the materialised table `dim_target_product_group_by_sale` (same allocation idea).

# Grain and key

One row per target row x allocation: unique over company, owner SKs, TargetProductGroupSK, RateTargetSK, ProductMktSK, Year, Month, group/segment IDs, ChannelTargetGroup, TargetID, EmployeeID, DepartmentID (enforced by QUALIFY ROW_NUMBER ordered by report segment). `TargetBySaleSK` is a generated sequence, not a stable key.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetBySaleSK` | INT64 | SK of the target-by-sales row: ROW_NUMBER over TargetProductGroupSK, RateTargetSK; regenerated on every query. |
| `SaleRepSKLast` | INT64 | SK of the target owner in dim_sale_representative_last, matched by EmployeeID + DepartmentID + CompanySK; for owners with no department match falls back to the row with NULL DepartmentID for the same employee. |
| `DepartmentSKLast` | INT64 | SK of the owner's department in dim_department_last. |
| `RegionSKLast` | INT64 | SK of the owner's region in dim_region_last. |
| `RegionManagerSKLast` | INT64 | SK of the region manager in dim_region_manager_last. |
| `SectionSKLast` | INT64 | SK of the owner's section in dim_section_last. |
| `SectionManagerSKLast` | INT64 | SK of the section manager in dim_section_manager_last. |
| `DirectorSKLast` | INT64 | SK of the director in dim_director_last (through the region). |
| `ReportSK` | INT64 | SK of the report row in dim_report chosen by region (and marketing group when the region has several report rows); NULL when none. |
| `TargetProductGroupSK` | INT64 | SK of the target row in dim_target_product_group. |
| `RateTargetSK` | INT64 | SK of the allocation-rate row in dim_rate_target; NULL for an unmatched branch row, even when another branch allocated the same target. |
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
| `CalQty` | FLOAT64 | Allocated target quantity = Qty x Percent / 100. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_target_by_agent.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_target_product_group](/dimension/dim_target_product_group.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_report](/dimension/dim_report.md), [dimension_table.dim_rate_target](/dimension/dim_rate_target.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_target_product_group, dim_product_mkt, dim_report, dim_rate_target, dim_sale_representative_last, dim_department_last, dim_region_last, dim_section_last, dim_region_manager_last, dim_section_manager_last. A view, so it recomputes on every query (heavy joins).

# Examples

Allocated target amount per salesperson for a month:

```sql
SELECT EmployeeID, SUM(CalAmt) AS target_amt, SUM(CalQty) AS target_qty
FROM `databuffet-nonprd.dimension_view.view_dim_target_by_agent`
WHERE companyID = 'ag01' AND Year = 2026 AND Month = 10
GROUP BY EmployeeID
```

Target per marketing group for a year:

```sql
SELECT MarketingGroupName, SUM(CalAmt) AS target_amt
FROM `databuffet-nonprd.dimension_view.view_dim_target_by_agent`
WHERE Year = 2026
GROUP BY MarketingGroupName
```

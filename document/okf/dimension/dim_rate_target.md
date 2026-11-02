---
type: BigQuery Table
title: "dim_rate_target"
description: "One row = one target-share rule: the percent of a target (TargetID, optionally by product group and month) assigned to one employee in one department of a company, from the MDS target rate master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_rate_target&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_rate_target
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_rate_target.sqlx"
    title: "Dataform definition (dimension/dim_rate_target.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Allocation rules that split the company-level product-group targets in [dim_target_product_group](/dimension/dim_target_product_group.md) among sales employees. `dim_target_product_group_by_sale` multiplies the target Amt and Qty by `Percent / 100` to get `CalAmt` / `CalQty`, and `dim_target_product_group_by_sale_dayofwork` and `view_dim_target_by_agent` build on it.

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md).

# Grain and key

One row per active MDS row, SK ordered by companyID, Year, Month, ProductGroupID, TargetID, TargetDepartmentID, DepartmentID, EmployeeID. Downstream code uses three rule shapes: Month NULL and ProductGroupID NULL (applies to the whole year), Month set and ProductGroupID NULL (applies to a month), Month and ProductGroupID both set (applies to a marketing group in a month). No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `RateTargetSK` | INT64 | Surrogate key, `ROW_NUMBER()` over the key columns above. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `Year` | INT64 | Target year (INT64 via `castInt64`). |
| `Month` | INT64 | Target month 1-12 (INT64 via `castInt64`); NULL means the rule covers the whole year. |
| `StartDate` | DATE | First date the rule applies (MDS `startdate`); `dim_target_product_group_by_sale_dayofwork` spreads the target over the days in the range. |
| `EndDate` | DATE | Last date the rule applies (MDS `enddate`). |
| `ProductGroupID` | STRING | Marketing group code the rule is limited to; matched to `dim_target_product_group.MarketingGroupID`. NULL means all groups. |
| `ProductGroupName` | STRING | Name of that group. |
| `TargetID` | STRING | Target code; joins to `dim_target_product_group.TargetID` (with CompanySK). |
| `TargetName` | STRING | Name of the target. |
| `TargetDepartmentID` | STRING | Code of the department group the rate rule is set for (e.g. `BT`); used only in the SK ordering. |
| `TargetDepartmentName` | STRING | Name of the target department; empty in current data. |
| `DepartmentID` | STRING | Department of the employee receiving the share; joins to dim_department_last / dim_department.DepartmentID. |
| `EmployeeID` | STRING | Employee (sales person) code receiving the share. |
| `EmployeeName` | STRING | Employee name as entered in MDS. |
| `Percent` | FLOAT64 | Share of the target in percent (FLOAT64 via `castFloat64`; the consumer divides by 100). For departments under director 'MDT' it is overwritten after the build with 100 divided by the number of distinct employee-department pairs for the same year, month and TargetID. |
| `MdsID` | STRING | `id` of the source row in `mds_data_target_rate_master`; trace column. |

# How it is built

- Definition: `definitions/dimension/dim_rate_target.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `RateTargetSK`.
- Storage options: `{"clusterBy": ["RateTargetSK"]}`.
- Reads: `mds_dataset.mds_data_target_rate_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`, reads `mds_data_target_rate_master`; a `post_operations` block then recalculates `Percent` for MDT departments. Config dependencies: dim_company, dim_department_last, dim_director_last and `update_sk_sale_rep_group` (the post-step follows the DirectorSK backfill).
- Approximate size (BigQuery metadata, 2026-10-31): 5,216 rows, 808.9 KB.

# Examples

Share rules for one target in a month.

```sql
SELECT companyID, Year, Month, TargetID, DepartmentID, EmployeeID, Percent
FROM `databuffet-nonprd.dimension_table.dim_rate_target`
WHERE Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
  AND Month = EXTRACT(MONTH FROM CURRENT_DATE('Asia/Bangkok'))
ORDER BY TargetID, DepartmentID, EmployeeID;
```

Share totals per target.

```sql
SELECT companyID, Year, Month, TargetID, ProductGroupID, ROUND(SUM(Percent), 2) AS total_percent
FROM `databuffet-nonprd.dimension_table.dim_rate_target`
GROUP BY 1, 2, 3, 4, 5
ORDER BY 1, 2, 3, 4;
```

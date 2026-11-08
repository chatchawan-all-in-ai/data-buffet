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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Allocation rules that split the company-level product-group targets in [dim_target_product_group](/dimension/dim_target_product_group.md) among sales employees. `dim_target_product_group_by_sale` multiplies the target Amt and Qty by `Percent / 100` to get `CalAmt` / `CalQty`, and `dim_target_product_group_by_sale_dayofwork` and `view_dim_target_by_agent` build on it.

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md).

# Grain and key

One row = one active MDS row. Natural key: (`companyID`, `Year`, `Month`, `StartDate`, `EndDate`, `ProductGroupID`, `TargetID`, `TargetDepartmentID`, `DepartmentID`, `EmployeeID`). `RateTargetSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `RateTargetSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
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
| `TargetDepartmentName` | STRING | Name of the target department. |
| `DepartmentID` | STRING | Department of the employee receiving the share; joins to dim_department_last / dim_department.DepartmentID. |
| `EmployeeID` | STRING | Employee (sales person) code receiving the share. |
| `EmployeeName` | STRING | Employee name as entered in MDS. |
| `Percent` | FLOAT64 | Share of the target in percent (FLOAT64 via `castFloat64`; the consumer divides by 100). After the build, rows with the same Year, Month (not NULL) and TargetID as a row whose department belongs to director 'MDT' get 100 divided by the number of distinct EmployeeID-DepartmentID pairs among those MDT rows. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_target_rate_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_rate_target.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_target_rate_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company, dim_department_last, dim_director_last and `update_sk_sale_rep_group`. A `post_operations` block then recalculates `Percent` using the rule in the [schema](#schema).
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

---
type: BigQuery Table
title: "dim_department"
description: "One row = one sales department (company, region, section, department id) with its validity period, from the MDS sales-department master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_department&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_department.sqlx"
    title: "Dataform definition (dimension/dim_department.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Sales organisation hierarchy leaf: each department belongs to a section and region and is valid for a date range (StartDate to EndDate), so reorganisations are kept as separate rows. Consumers: [dim_department_last](/dimension/dim_department_last.md) (latest-row snapshot), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [view_dim_sale_representative](/view/dimension_view/view_dim_sale_representative.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md) and [fact_transcation](/fact/fact_transcation.md). Source: mds `mds_data_sales_department_master`.

# Grain and key

One row per (company, RegionID, SectionID, DepartmentID, StartDate, EndDate) among active mds rows. Key: `DepartmentSK` (surrogate, unstable across days). The same DepartmentID can appear in several rows with different periods.

# Schema

| Column | Type | Description |
|---|---|---|
| `DepartmentSK` | INT64 | `DepartmentSK` is `ROW_NUMBER() OVER(ORDER BY companyID, RegionID, SectionID, DepartmentID, StartDate, EndDate)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `RegionID` | STRING | Pass-through of mds `RegionID`, cleaned with `cleanString` (empty string becomes NULL). Region code the department belongs to. |
| `SectionID` | STRING | Pass-through of mds `SectionID`, cleaned with `cleanString` (empty string becomes NULL). Section code the department belongs to. |
| `DepartmentID` | STRING | Pass-through of mds `DepartmentID`, cleaned with `cleanString` (empty string becomes NULL). Department code; key of the department within a company and joins to sale-representative rows. |
| `DepartmentName` | STRING | Pass-through of mds `DepartmentName`, cleaned with `cleanString` (empty string becomes NULL). Department name. |
| `StartDate` | DATE | First day this department assignment (region/section) is valid (mds `StartDate`, DATE). |
| `EndDate` | DATE | Last day it is valid (mds `EndDate`, DATE). |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_department.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `DepartmentSK`.
- Storage options: `{"clusterBy": ["DepartmentSK"]}`.
- Reads: `mds_dataset.mds_data_sales_department_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows (`is_active = TRUE`); runs after dim_company (declared dependency).
- Approximate size (BigQuery metadata, 2026-10-31): 378 rows, 41.1 KB.

# Examples

Departments valid today with their section and region.

```sql
SELECT companyID, RegionID, SectionID, DepartmentID, DepartmentName
FROM `databuffet-nonprd.dimension_table.dim_department`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

Departments that changed section over time.

```sql
SELECT companyID, DepartmentID, COUNT(DISTINCT SectionID) AS sections
FROM `databuffet-nonprd.dimension_table.dim_department`
GROUP BY 1, 2
HAVING sections > 1;
```

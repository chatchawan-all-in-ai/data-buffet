---
type: BigQuery Table
title: "dim_department"
description: "One row = one sales department (company, region, section, department id) with its validity period, from the MDS sales-department master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_department&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_department
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_department.sqlx"
    title: "Dataform definition (dimension/dim_department.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Sales organisation hierarchy leaf: each department belongs to a section and region and is valid for a date range (StartDate to EndDate), so reorganisations are kept as separate rows. Source: mds `mds_data_sales_department_master`.

Read by: [dim_department_last](/dimension/dim_department_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [fact_transcation](/fact/fact_transcation.md), [view_dim_sale_representative](/view/dimension_view/view_dim_sale_representative.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md).

# Grain and key

One row = one department period. Natural key: (`companyID`, `RegionID`, `SectionID`, `DepartmentID`, `StartDate`, `EndDate`). `DepartmentSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `DepartmentSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `RegionID` | STRING | Pass-through of mds `RegionID`, cleaned with `cleanString` (empty string becomes NULL). Region code the department belongs to. |
| `SectionID` | STRING | Pass-through of mds `SectionID`, cleaned with `cleanString` (empty string becomes NULL). Section code the department belongs to. |
| `DepartmentID` | STRING | Pass-through of mds `DepartmentID`, cleaned with `cleanString` (empty string becomes NULL). Department code; key of the department within a company and joins to sale-representative rows. |
| `DepartmentName` | STRING | Pass-through of mds `DepartmentName`, cleaned with `cleanString` (empty string becomes NULL). Department name. |
| `StartDate` | DATE | First day this department assignment (region/section) is valid (mds `StartDate`, DATE). |
| `EndDate` | DATE | Last day it is valid (mds `EndDate`, DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_sales_department_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_department.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_sales_department_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
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

---
type: BigQuery View
title: "view_rls_data"
description: "One row = one (employee, restricted attribute, allowed value) entry of the organisation-based row-level-security map for sales managers, plus one CompanyID row per employee."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=view_rls_data&page=table"
tags: ["view", "process_dataset"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/process_dataset/view_rls_data.sqlx"
    title: "Dataform definition (view/process_dataset/view_rls_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The organisation-hierarchy part of the row-level-security (RLS) access map. From the latest org dims ([dim_director_last](/dimension/dim_director_last.md), [dim_region_last](/dimension/dim_region_last.md), [dim_section_last](/dimension/dim_section_last.md) and their manager dims) it lists, for every director of sales, region manager and section manager, which directors, regions and sections they may see (a director sees all regions and sections under their director, a region manager the sections under the region and so on), plus the company they belong to (`LevelName = 'CompanyID'`, `level_data = 9`). [view_rls_sale_data](/view/process_dataset/view_rls_sale_data.md) maps `EmployeeID` to e-mail and adds customer rows for Power BI RLS.

Used by [process_dataset.view_rls_sale_data](/view/process_dataset/view_rls_sale_data.md).

# Grain and key

One row per distinct (EmployeeID, EmployeeLevel, LevelName, LevelValue, level_data). Employees missing one of the three levels (`emp_wrong`) get filler rows with `LevelValue = 'All'`; every employee also has one `CompanyID` row (`level_data = 9`). Output is ordered by EmployeeID, level_data descending, LevelValue.

# Schema

| Column | Type | Description |
|---|---|---|
| `EmployeeID` | STRING | Employee id of the director of sales (`DirectorOfSalesID`), region manager (`RegionManagerEmployeeID`) or section manager (`SectionManagerEmployeeID`) from the `*_last` dims; maps to `EmployeeID` in `mds_data_org_employee_mapping_center`. |
| `EmployeeLevel` | INT64 | Highest organisation level of the employee: 4 = director, 3 = region manager, 2 = section manager; NULL on rows built only for the company filter if the employee has no level. |
| `LevelName` | STRING | Which attribute is restricted: `DirectorID`, `RegionID`, `SectionID`, or `CompanyID`. |
| `LevelValue` | STRING | Allowed value for that attribute (director id, region id, section id, or the company's `CompanyReportID`); `All` for a level the employee has no row for. |
| `level_data` | INT64 | Numeric level of the attribute: 4 = DirectorID, 3 = RegionID, 2 = SectionID, 9 = the CompanyID rows appended at the end. |

# How it is built

- Definition: `definitions/view/process_dataset/view_rls_data.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md), [dimension_view.view_dim_company](/view/dimension_view/view_dim_company.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `dim_director_last`, `dim_region_last`, `dim_region_manager_last`, `dim_section_last`, `dim_section_manager_last`, `dim_sale_representative_last` and `view_dim_company` (dims rebuilt in `dimension_daily`).

# Examples

What can one employee see.

```sql
SELECT EmployeeID, EmployeeLevel, LevelName, LevelValue
FROM `databuffet-nonprd.process_dataset.view_rls_data`
WHERE EmployeeID = '<employee id>'
ORDER BY level_data DESC, LevelValue
```

Employees per level.

```sql
SELECT EmployeeLevel, COUNT(DISTINCT EmployeeID) AS employees
FROM `databuffet-nonprd.process_dataset.view_rls_data`
GROUP BY EmployeeLevel
ORDER BY EmployeeLevel
```

---
type: BigQuery View
title: "view_dim_sale_representative_last"
description: "One row = one sales representative in the latest-organisation snapshot (SaleRepSK) with department name and a per-region sort number."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_sale_representative_last&page=table"
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_sale_representative_last.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_sale_representative_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Current-organisation ('last') sales representative view: [dim_sale_representative_last](/dimension/dim_sale_representative_last.md) joined to [dim_department_last](/dimension/dim_department_last.md) for `DepartmentName`, plus a `Sort` column for report ordering (added by a team member). The `_last` family always shows the latest org chart (each employee at their latest department/section/region), unlike the date-versioned dims. Used by [view_sales_representative_last](/view/dimension_view/view_sales_representative_last.md), and the `_last` SKs are used by the target and customer-report-info models.

# Grain and key

One row per SaleRepSK of the `_last` dim; the department join is on DepartmentSK + CompanySK. Some representatives have no department (NULL DepartmentSK/DepartmentID).

# Schema

| Column | Type | Description |
|---|---|---|
| `SaleRepSK` | INT64 | SK of the representative in dim_sale_representative_last. |
| `DepartmentSK` | INT64 | SK of the representative's department in [dim_department_last](/dimension/dim_department_last.md); NULL when the department is not resolved. |
| `SectionSK` | INT64 | SK of the section in `dim_section_last`, taken through the department; NULL when unresolved. |
| `SectionManagerSK` | INT64 | SK of the section manager in `dim_section_manager_last`; NULL when unresolved. |
| `RegionSK` | INT64 | SK of the region in `dim_region_last`, taken through the department; NULL when unresolved. |
| `RegionManagerSK` | INT64 | SK of the region manager in `dim_region_manager_last`; NULL when unresolved. |
| `DirectorSK` | INT64 | SK of the director in `dim_director_last`; NULL when unresolved. |
| `CompanySK` | INT64 | SK of the company in [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code (ag01/aa05/ab01/ac02/ak02). |
| `DepartmentID` | STRING | Department code of the representative (department_id in MAC5); NULL for rows without a department. |
| `EmployeeID` | STRING | Employee (salesperson) code, `percode` in MAC5. |
| `EmployeeName` | STRING | First name, parsed from the MAC5 `pernamet` text (first token). |
| `EmployeeSurname` | STRING | Surname, parsed from `pernamet` (second token). |
| `EmployeeNickname` | STRING | Nickname, parsed from the parenthesised part of `pernamet`. |
| `DepCode` | STRING | Department/channel code used to map to channel dimensions ([view_dim_channel](/view/dimension_view/view_dim_channel.md) `DepCode`). |
| `CostChannelID` | STRING | Cost channel code of the representative (pass-through from the dimension). |
| `ProvinceID` | STRING | Province code of the representative (pass-through from the dimension). |
| `ChangeSectionFlag` | STRING | Flag from the dimension marking a representative who changed section (pass-through; exact values not documented in the repo). |
| `CustomerFlag` | STRING | Flag from the dimension (pass-through; exact meaning not documented in the repo, likely marks customer-owning representatives, inferred from the name). |
| `DepartmentName` | STRING | Department name, joined from the department dimension. |
| `Sort` | STRING | Two-digit running number (`FORMAT('%02d', ROW_NUMBER())`) per RegionSK, ordered by DepartmentID then EmployeeID; added for report sorting. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_sale_representative_last.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_sale_representative_last and dim_department_last (tag `dimension_daily`, `*_last` snapshot family; dimension/special-cases.md).

# Examples

Representatives of one region ordered for display:

```sql
SELECT EmployeeID, DepartmentName, Sort
FROM `databuffet-nonprd.dimension_view.view_dim_sale_representative_last`
WHERE RegionSK = 1
ORDER BY Sort
```

Representatives without a department:

```sql
SELECT companyID, EmployeeID
FROM `databuffet-nonprd.dimension_view.view_dim_sale_representative_last`
WHERE DepartmentSK IS NULL
```

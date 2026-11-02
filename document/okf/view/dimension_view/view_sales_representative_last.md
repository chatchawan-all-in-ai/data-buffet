---
type: BigQuery View
title: "view_sales_representative_last"
description: "One row = one sales-representative assignment rule in the latest organisation, with department, section and region IDs and names resolved; an employee can have several rows."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_sales_representative_last&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_sales_representative_last
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_sales_representative_last.sqlx"
    title: "Dataform definition (view/dimension_view/view_sales_representative_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Wide convenience view over [view_dim_sale_representative_last](/view/dimension_view/view_dim_sale_representative_last.md): re-joins [dim_department_last](/dimension/dim_department_last.md), [dim_section_last](/dimension/dim_section_last.md) and [dim_region_last](/dimension/dim_region_last.md) to add RegionID/RegionName and SectionID/SectionName (via the department's SectionSK/RegionSK) so one table carries the whole org path of a salesperson. Nothing else in the repo reads it; used by BI.

# Grain and key

One row per SaleRepSK assignment rule (same grain as view_dim_sale_representative_last); all joins are LEFT on SK + CompanySK. Normal and order-window rules can retain multiple SaleRepSK rows for one EmployeeID in a region.

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
| `ChangeSectionFlag` | STRING | Section-change flag from the dimension: `Yes` on change-of-section rows, NULL otherwise. |
| `CustomerFlag` | STRING | List of customer codes, joined by the pipe character, that the representative rule also applies to; NULL when the rule is not limited to customers. |
| `StartDate` | DATE | Start of the validity period of this representative/department assignment (pass-through). |
| `EndDate` | DATE | End of the validity period of this assignment (pass-through). |
| `Sort` | STRING | Two-digit running number (`FORMAT('%02d', ROW_NUMBER())`) per RegionSK, ordered by DepartmentID then EmployeeID; added for report sorting. |
| `RegionID` | STRING | Region code from dim_region_last (via the department's RegionSK). |
| `RegionName` | STRING | Region name from dim_region_last. |
| `SectionID` | STRING | Section code from dim_section_last (via the department's SectionSK). |
| `SectionName` | STRING | Section name from dim_section_last. |
| `DepartmentName` | STRING | Department name from dim_department_last. |

# How it is built

- Definition: `definitions/view/dimension_view/view_sales_representative_last.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_view.view_dim_sale_representative_last](/view/dimension_view/view_dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads view_dim_sale_representative_last (a view deployed first) and the three `_last` dims. Tag `view`.

# Examples

Org path of every representative of a company:

```sql
SELECT EmployeeID, DepartmentName, SectionName, RegionName
FROM `databuffet-nonprd.dimension_view.view_sales_representative_last`
WHERE companyID = 'ag01'
```

Distinct representatives per region for one company:

```sql
SELECT RegionName, COUNT(DISTINCT EmployeeID) AS reps
FROM `databuffet-nonprd.dimension_view.view_sales_representative_last`
WHERE companyID = 'ag01'
GROUP BY RegionName
```

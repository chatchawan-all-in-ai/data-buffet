---
type: BigQuery View
title: "view_dim_sale_representative"
description: "One row = one sales representative assignment (SaleRepSK: employee x department x validity period) with the department name."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_sale_representative&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_sale_representative
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_sale_representative.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_sale_representative.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Time-versioned sales representative dimension: [dim_sale_representative](/dimension/dim_sale_representative.md) joined to [dim_department](/dimension/dim_department.md) for the department name. The versioned (StartDate/EndDate) variant, as opposed to the `_last` snapshot [view_dim_sale_representative_last](/view/dimension_view/view_dim_sale_representative_last.md). Used by BI for point-in-time sales ownership.

# Grain and key

One row per SaleRepSK (`select distinct`); the join to dim_department is on DepartmentID + CompanySK, which can in principle match several department periods; DISTINCT collapses identical duplicates only.

# Schema

| Column | Type | Description |
|---|---|---|
| `SaleRepSK` | INT64 | SK of the sales representative assignment in dim_sale_representative (full rebuild, regenerated daily). |
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
| `DepartmentName` | STRING | Department name from dim_department (matched on DepartmentID + CompanySK). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_sale_representative.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_department](/dimension/dim_department.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_sale_representative and dim_department (full-rebuild tables, tag `dimension_daily`).

# Examples

Active assignments today in one company:

```sql
SELECT EmployeeID, DepartmentID, DepartmentName
FROM `databuffet-nonprd.dimension_view.view_dim_sale_representative`
WHERE companyID = 'ag01' AND CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
```

Representatives per department:

```sql
SELECT DepartmentName, COUNT(DISTINCT EmployeeID) AS reps
FROM `databuffet-nonprd.dimension_view.view_dim_sale_representative`
GROUP BY DepartmentName
```

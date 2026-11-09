---
type: BigQuery View
title: "export_view_dim_sale_representative_last"
description: "One row = one sales representative record in its latest period, exposed for the Pub/Sub export of dimension_view.view_dim_sale_representative_last with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_sale_representative_last&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_sale_representative_last
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_sale_representative_last.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_sale_representative_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_sale_representative_last](/view/dimension_view/view_dim_sale_representative_last.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_sale_representative_last`.

# Grain and key

One row = one sales representative record in its latest period: key `companyID`, `DepartmentID`, `EmployeeID`, `DepCode`, `CostChannelID`, `ProvinceID`, `OrderStartDate`, `OrderEndDate` (unique); `row_key` is the JSON of that key. `companyID`, `DepCode`, `CostChannelID`, `ProvinceID`, `OrderStartDate`, `OrderEndDate` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `SaleRepSK` | INT64 | SK of the representative in dim_sale_representative_last. |
| `EmployeeID` | STRING | Employee (salesperson) code, `percode` in MAC5. |
| `EmployeeName` | STRING | First name, parsed from the MAC5 `pernamet` text (first token). |
| `EmployeeSurname` | STRING | Surname, parsed from `pernamet` (second token). |
| `EmployeeNickname` | STRING | Nickname, parsed from the parenthesised part of `pernamet`. |
| `DepartmentID` | STRING | Department code of the representative (department_id in MAC5); NULL for rows without a department. |
| `DepartmentName` | STRING | Department name, joined from the department dimension. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_sale_representative_last.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_sale_representative_last](/view/dimension_view/view_dim_sale_representative_last.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_sale_representative_last`
GROUP BY row_key
HAVING n > 1
```

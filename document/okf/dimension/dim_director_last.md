---
type: BigQuery Table
title: "dim_director_last"
description: "One row = the latest-period row of each director per company, taken from dim_director."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_director_last&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_director_last
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_director_last.sqlx"
    title: "Dataform definition (dimension/dim_director_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Snapshot of [dim_director](/dimension/dim_director.md) keeping, for each (CompanyID, DirectorID), the row with the latest `EndDate` then `StartDate`.

Read by: [dim_rate_target](/dimension/dim_rate_target.md), [org_center_member](/org_center/org_center_member.md), [org_center_unit](/org_center/org_center_unit.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_rls_data](/view/process_dataset/view_rls_data.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), update_sk_sale_rep_group.

# Grain and key

One row = the latest-period row of a director: key (company, DirectorID). `DirectorSK` is `ROW_NUMBER() OVER (ORDER BY CompanySK, DirectorID)`, regenerated every run and numbered independently of dim_director.

# Schema

| Column | Type | Description |
|---|---|---|
| `DirectorSK` | INT64 | `ROW_NUMBER() OVER (ORDER BY CompanySK, DirectorID)`. Regenerated every run; differs from `dim_director.DirectorSK`. `dim_department_last.DirectorSK` is backfilled to point at this value. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code from dim_company. |
| `DirectorID` | STRING | Director code, pass-through from dim_director. |
| `DirectorName` | STRING | Director name, pass-through from dim_director. |
| `DirectorOfSalesID` | STRING | Director-of-sales code, pass-through from dim_director. |
| `DirectorOfSalesName` | STRING | Director-of-sales name, pass-through from dim_director. |
| `StartDate` | DATE | StartDate of the chosen (latest) dim_director period. |
| `EndDate` | DATE | EndDate of the chosen (latest) dim_director period; may be in the past. |

# How it is built

- Definition: `definitions/dimension/dim_director_last.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `DirectorSK`.
- Storage options: `{"clusterBy": ["DirectorSK"]}`.
- Reads: [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Rows are chosen with `QUALIFY ROW_NUMBER() OVER (PARTITION BY CompanyID, DirectorID ORDER BY EndDate DESC, StartDate DESC) = 1`.
- The `update_sk_sale_rep_group` step fills `dim_region_last.DirectorSK` from this table on `DirectorID` + `CompanySK`; `dim_department_last` then copies that key.
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company and dim_director.

# Examples

One row per director with their director of sales.

```sql
SELECT companyID, DirectorID, DirectorName, DirectorOfSalesID, EndDate
FROM `databuffet-nonprd.dimension_table.dim_director_last`
ORDER BY companyID, DirectorID;
```

Department snapshot with its director snapshot.

```sql
SELECT d.companyID, d.DepartmentID, dr.DirectorName
FROM `databuffet-nonprd.dimension_table.dim_department_last` d
LEFT JOIN `databuffet-nonprd.dimension_table.dim_director_last` dr ON d.DirectorSK = dr.DirectorSK;
```

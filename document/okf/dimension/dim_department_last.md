---
type: BigQuery Table
title: "dim_department_last"
description: "One row = the latest-period row of each department per company, taken from dim_department, with placeholder FK columns for section, region and director."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_department_last&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_department_last
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_department_last.sqlx"
    title: "Dataform definition (dimension/dim_department_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Snapshot of [dim_department](/dimension/dim_department.md) keeping, for each (CompanyID, DepartmentID), the row with the latest `EndDate` then latest `StartDate`. The columns `SectionSK`, `SectionManagerSK`, `RegionSK`, `RegionManagerSK` and `DirectorSK` are created as NULL by this build and backfilled afterwards by the `update_sk_sale_rep_group` step.

Read by: [dim_customer_report_info](/dimension/dim_customer_report_info.md), [dim_rate_target](/dimension/dim_rate_target.md), [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_sale_representative_last](/view/dimension_view/view_dim_sale_representative_last.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_sales_representative_last](/view/dimension_view/view_sales_representative_last.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = the latest-period row of a department. Natural key: (`companyID`, `DepartmentID`, `StartDate`, `EndDate`). `DepartmentSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `DepartmentSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `SectionSK` | INT64 | Foreign key to the section `_last` dimension; created as NULL by this build and filled by the later `update_sk_sale_rep_group` UPDATE step. |
| `SectionManagerSK` | INT64 | Foreign key to the section-manager `_last` dimension; NULL at build, backfilled by `update_sk_sale_rep_group`. |
| `RegionSK` | INT64 | Foreign key to the region `_last` dimension; NULL at build, backfilled by `update_sk_sale_rep_group`. |
| `RegionManagerSK` | INT64 | Foreign key to the region-manager `_last` dimension; NULL at build, backfilled by `update_sk_sale_rep_group`. |
| `DirectorSK` | INT64 | Foreign key to [dim_director_last](/dimension/dim_director_last.md); NULL at build, backfilled by `update_sk_sale_rep_group` (dim_rate_target depends on that backfill for its MDT logic). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code from dim_company. |
| `RegionID` | STRING | Region code, pass-through from dim_department. |
| `SectionID` | STRING | Section code, pass-through from dim_department. |
| `DepartmentID` | STRING | Department code, pass-through from dim_department; with company it is the row key. |
| `DepartmentName` | STRING | Department name, pass-through from dim_department. |
| `StartDate` | DATE | StartDate of the chosen (latest) dim_department period. |
| `EndDate` | DATE | EndDate of the chosen (latest) dim_department period; it may be in the past for departments that were closed. |
# How it is built

- Definition: `definitions/dimension/dim_department_last.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: [dimension_table.dim_department](/dimension/dim_department.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Rows are chosen with `QUALIFY ROW_NUMBER() OVER (PARTITION BY CompanyID, DepartmentID ORDER BY EndDate DESC, StartDate DESC) = 1`.
- The five FK SK columns are filled afterwards by the separate `update_sk_sale_rep_group` operation, which depends on all `_last` tables.
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company and dim_department.
# Examples

Latest department rows with their resolved director FK.

```sql
SELECT companyID, DepartmentID, DepartmentName, SectionID, RegionID, DirectorSK
FROM `databuffet-nonprd.dimension_table.dim_department_last`
ORDER BY companyID, DepartmentID;
```

Rows still without a director after FK backfill.

```sql
SELECT COUNT(*) AS missing_director
FROM `databuffet-nonprd.dimension_table.dim_department_last`
WHERE DirectorSK IS NULL;
```

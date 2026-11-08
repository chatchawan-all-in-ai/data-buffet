---
type: BigQuery Table
title: "dim_grade"
description: "One row = one grade band (min/max score percentage, grade label, validity period) per company, used to turn a customer's total score into a grade."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_grade&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_grade
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_grade.sqlx"
    title: "Dataform definition (dimension/dim_grade.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Final lookup of the customer-grade model: maps a customer's total score percentage to a `Grade` label. [dim_customer_grade](/dimension/dim_customer_grade.md) and [dim_group_customer_grade](/dimension/dim_group_customer_grade.md) each join it twice, on `CompanySK` and `Percentmin`..`Percentmax` with no date condition, and store `InvoiceGradeSK` and `DueGradeSK` (grade based on the invoice-date and due-date scoring); only the rows of the current year (year of yesterday) are recomputed, so older rows keep the SK from their last run. Source is mds `mds_data_custgrade_master`.

Read by: [dim_customer_grade](/dimension/dim_customer_grade.md), [dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row = one grade band. Natural key: (`companyID`, `Percentmin`, `Percentmax`, `StartDate`, `EndDate`). `GradeSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `GradeSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `Percentmin` | FLOAT64 | Lower bound (inclusive) of the band for the customer's total score percentage, cast with `castFloat64` from the mds column. |
| `Percentmax` | FLOAT64 | Upper bound (inclusive) of the band for the customer's total score percentage, cast with `castFloat64` from the mds column. |
| `Grade` | STRING | Grade label (as entered in MDS) assigned to scores inside the band; `cleanString` of the mds `Grade` column. |
| `StartDate` | DATE | First day the band row is valid (mds `StartDate`, passed through as DATE). |
| `EndDate` | DATE | Last day the band row is valid (mds `EndDate`, passed through as DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_custgrade_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_grade.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_custgrade_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Grade bands valid today.

```sql
SELECT companyID, Grade, Percentmin, Percentmax
FROM `databuffet-nonprd.dimension_table.dim_grade`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
ORDER BY companyID, Percentmin;
```

Grade for a total score of 72 percent.

```sql
SELECT Grade
FROM `databuffet-nonprd.dimension_table.dim_grade`
WHERE companyID = 'ag01' AND 72 BETWEEN Percentmin AND Percentmax
  AND CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

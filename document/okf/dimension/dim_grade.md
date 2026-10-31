---
type: BigQuery Table
title: "dim_grade"
description: "One row = one grade band (min/max score percentage, grade label, validity period) per company, used to turn a customer's total score into a grade."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_grade&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_grade.sqlx"
    title: "Dataform definition (dimension/dim_grade.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Final lookup of the customer-grade model: maps a customer's total score percentage to a `Grade` label. [dim_customer_grade](/dimension/dim_customer_grade.md) joins it twice and stores `InvoiceGradeSK` and `DueGradeSK` (grade based on the invoice-date and due-date scoring); [dim_group_customer_grade](/dimension/dim_group_customer_grade.md) also uses it. Source is mds `mds_data_custgrade_master`.

# Grain and key

One row per (company, Percentmin, Percentmax, StartDate, EndDate) band from mds. Key: `GradeSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `GradeSK` | INT64 | `GradeSK` is `ROW_NUMBER() OVER(ORDER BY companyID, Percentmin, Percentmax, StartDate, EndDate)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `Percentmin` | FLOAT64 | Lower bound (inclusive) of the band for the customer's total score percentage, cast with `castFloat64` from the mds column. |
| `Percentmax` | FLOAT64 | Upper bound (inclusive) of the band for the customer's total score percentage, cast with `castFloat64` from the mds column. |
| `Grade` | STRING | Grade label (as entered in MDS) assigned to scores inside the band; `cleanString` of the mds `Grade` column. |
| `StartDate` | DATE | First day the band row is valid (mds `StartDate`, passed through as DATE). |
| `EndDate` | DATE | Last day the band row is valid (mds `EndDate`, passed through as DATE). dim_customer_grade matches rows where yesterday (Asia/Bangkok) is between StartDate and EndDate. |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_grade.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `GradeSK`.
- Storage options: `{"clusterBy": ["GradeSK"]}`.
- Reads: `mds_dataset.mds_data_custgrade_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows; runs after dim_company. dim_customer_grade lists it as a dependency and refreshes its stored `*GradeSK` values from it.
- Approximate size (BigQuery metadata, 2026-10-31): 30 rows, 2.8 KB.

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

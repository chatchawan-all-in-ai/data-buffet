---
type: BigQuery Table
title: "dim_bounce_cheque_score"
description: "One row = one score band (min/max count of cancelled/bounced cheques, validity period) per company, used to score a customer's cheque reliability."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_bounce_cheque_score&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_bounce_cheque_score
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_bounce_cheque_score.sqlx"
    title: "Dataform definition (dimension/dim_bounce_cheque_score.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Scoring-band lookup for the customer-grade model. A customer earns `Score` points when its yearly count of cancelled cheques (`cancel_chq` in dim_customer_grade) falls inside `[BouncedChequeMin, BouncedChequeMax]`. Consumers: [dim_customer_grade](/dimension/dim_customer_grade.md) (as `BounceChequeSK`) and [dim_group_customer_grade](/dimension/dim_group_customer_grade.md). Source is the mds master `mds_data_custgrade_cheque_score_master`.

# Grain and key

One row per (company, BouncedChequeMin, BouncedChequeMax, StartDate, EndDate) band from mds. Key: `BounceChequeSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `BounceChequeSK` | INT64 | `BounceChequeSK` is `ROW_NUMBER() OVER(ORDER BY companyID, BouncedChequeMin, BouncedChequeMax, StartDate, EndDate)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `BouncedChequeMin` | FLOAT64 | Lower bound (inclusive) of the band for the number of cancelled (bounced) cheques, cast with `castFloat64` from the mds column. |
| `BouncedChequeMax` | FLOAT64 | Upper bound (inclusive) of the band for the number of cancelled (bounced) cheques, cast with `castFloat64` from the mds column. |
| `Score` | FLOAT64 | Score points awarded to a customer whose metric falls inside the band; `castFloat64` of the mds `Score` column. [dim_customer_grade](/dimension/dim_customer_grade.md) uses `IFNULL(Score, 0)`. |
| `StartDate` | DATE | First day the band row is valid (mds `StartDate`, passed through as DATE). |
| `EndDate` | DATE | Last day the band row is valid (mds `EndDate`, passed through as DATE). dim_customer_grade matches rows where yesterday (Asia/Bangkok) is between StartDate and EndDate. |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_bounce_cheque_score.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `BounceChequeSK`.
- Storage options: `{"clusterBy": ["BounceChequeSK"]}`.
- Reads: `mds_dataset.mds_data_custgrade_cheque_score_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows; runs after dim_company.

# Examples

Bands valid today per company.

```sql
SELECT companyID, BouncedChequeMin, BouncedChequeMax, Score
FROM `databuffet-nonprd.dimension_table.dim_bounce_cheque_score`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
ORDER BY companyID, BouncedChequeMin;
```

Overlapping bands for the same company, active today.

```sql
SELECT a.companyID, a.MdsID, b.MdsID AS other_MdsID
FROM `databuffet-nonprd.dimension_table.dim_bounce_cheque_score` a
JOIN `databuffet-nonprd.dimension_table.dim_bounce_cheque_score` b
  ON a.companyID = b.companyID AND a.MdsID < b.MdsID
 AND a.BouncedChequeMin <= b.BouncedChequeMax AND b.BouncedChequeMin <= a.BouncedChequeMax
 AND CURRENT_DATE('Asia/Bangkok') BETWEEN a.StartDate AND a.EndDate
 AND CURRENT_DATE('Asia/Bangkok') BETWEEN b.StartDate AND b.EndDate;
```

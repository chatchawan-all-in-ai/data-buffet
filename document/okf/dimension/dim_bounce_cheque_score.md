---
type: BigQuery Table
title: "dim_bounce_cheque_score"
description: "One row = one score band (bounds and validity period) per company for the customer-grade CountCancelCheque metric."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T23:20:34+07:00" }
status: draft
---

# What it is

Scoring-band lookup for the customer-grade model. A customer earns `Score` points when its `CountCancelCheque` metric (defined in [dim_customer_grade](/dimension/dim_customer_grade.md#schema)) falls inside `[BouncedChequeMin, BouncedChequeMax]`; [dim_customer_grade](/dimension/dim_customer_grade.md) stores the matched band as `BounceChequeSK`. Source is the mds master `mds_data_custgrade_cheque_score_master`.

Read by: [dim_customer_grade](/dimension/dim_customer_grade.md), [dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row = one score band. Natural key: (`companyID`, `BouncedChequeMin`, `BouncedChequeMax`, `StartDate`, `EndDate`). `BounceChequeSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `BounceChequeSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `BouncedChequeMin` | FLOAT64 | Lower bound (inclusive) of the band for `CountCancelCheque` (see the metric definition linked above), cast with `castFloat64` from the mds column. |
| `BouncedChequeMax` | FLOAT64 | Upper bound (inclusive) of the band for `CountCancelCheque` (see the metric definition linked above), cast with `castFloat64` from the mds column. |
| `Score` | FLOAT64 | Score points awarded to a customer whose metric falls inside the band; `castFloat64` of the mds `Score` column. [dim_customer_grade](/dimension/dim_customer_grade.md) uses `IFNULL(Score, 0)`. |
| `StartDate` | DATE | First day the band row is valid (mds `StartDate`, passed through as DATE). |
| `EndDate` | DATE | Last day the band row is valid (mds `EndDate`, passed through as DATE). dim_customer_grade matches rows where yesterday (Asia/Bangkok) is between StartDate and EndDate. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_custgrade_cheque_score_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_bounce_cheque_score.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`).
- Reads: `mds_dataset.mds_data_custgrade_cheque_score_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
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

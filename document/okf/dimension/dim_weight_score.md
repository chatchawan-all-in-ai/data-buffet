---
type: BigQuery Table
title: "dim_weight_score"
description: "One row = one MDS weight-score lookup entry (score type with its weight) of a company over one StartDate to EndDate interval, from the MDS weight-score master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_weight_score&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_weight_score
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_weight_score.sqlx"
    title: "Dataform definition (dimension/dim_weight_score.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

MDS weight-score lookup: each row names a score type in English and Thai and gives its numeric weight.

# Grain and key

One row = one active MDS weight-score row: key `WeightSK`, `ROW_NUMBER()` ordered by CompanyID, Typeeng, Typethai, StartDate, EndDate. A score type that changes weight appears once per interval. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `WeightSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by CompanyID, Typeeng, Typethai, StartDate, EndDate. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `CompanyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `Typeeng` | STRING | Score type name in English. |
| `Typethai` | STRING | Score type name in Thai. |
| `weight` | FLOAT64 | Numeric weight of the score type from MDS; FLOAT64 via `castFloat64`. |
| `Remark` | STRING | Free-text remark from MDS. |
| `StartDate` | DATE | First date the weight applies (MDS DATE). |
| `EndDate` | DATE | Last date the weight applies (MDS DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_data_custgrade_weight_score_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_weight_score.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `WeightSK`.
- Storage options: `{"clusterBy": ["WeightSK"]}`.
- Reads: `mds_dataset.mds_data_custgrade_weight_score_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Weights valid today.

```sql
SELECT CompanyID, Typeeng, Typethai, weight, Remark
FROM `databuffet-nonprd.dimension_table.dim_weight_score`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

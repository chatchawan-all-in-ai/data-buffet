---
type: BigQuery Table
title: "dim_weight_score"
description: "One row = one customer-grade weight score entry (score type with its weight) of a company over one StartDate to EndDate interval, from the MDS weight-score master."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Weights used by the customer-grade scoring (source table `mds_data_custgrade_weight_score_master`): each row names a score type in English and Thai and gives its numeric weight. No definition in this repo reads it, so it is available for BI or ad-hoc scoring only.

No other definition in the repo reads it.

# Grain and key

One row per active MDS row, ordered and SK-numbered by CompanyID, Typeeng, Typethai, StartDate, EndDate. A score type that changes weight appears once per interval. Very small table. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `WeightSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by CompanyID, Typeeng, Typethai, StartDate, EndDate. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `CompanyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `Typeeng` | STRING | Score type name in English. |
| `Typethai` | STRING | Score type name in Thai. |
| `weight` | FLOAT64 | Weight in points of the score type in the customer-grade score (e.g. 20 for AverageCollectionday, 10 for Contactyear); FLOAT64 via `castFloat64`. |
| `Remark` | STRING | Free-text remark from MDS. |
| `StartDate` | DATE | First date the weight applies (MDS DATE). |
| `EndDate` | DATE | Last date the weight applies (MDS DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_data_custgrade_weight_score_master`; trace column. |

# How it is built

- Definition: `definitions/dimension/dim_weight_score.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `WeightSK`.
- Storage options: `{"clusterBy": ["WeightSK"]}`.
- Reads: `mds_dataset.mds_data_custgrade_weight_score_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; `CREATE OR REPLACE` each run from `mds_dataset` (loaded outside this repo). Runs after `dim_company`. Reads `mds_data_custgrade_weight_score_master`.
- Approximate size (BigQuery metadata, 2026-10-31): 5 rows, 747 B.

# Examples

Weights valid today.

```sql
SELECT CompanyID, Typeeng, Typethai, weight, Remark
FROM `databuffet-nonprd.dimension_table.dim_weight_score`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

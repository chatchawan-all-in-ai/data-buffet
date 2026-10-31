---
type: BigQuery Table
title: "dim_target_series_mdt"
description: "One row = the daily sales target (Amt, Qty) of one MDT branch for one product series on one date, derived by splitting the monthly MDS series target evenly over the days of the month, plus a reserved -1 row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_target_series_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_target_series_mdt
tags: ["dimension", "mds", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_target_series_mdt.sqlx"
    title: "Dataform definition (dimension/dim_target_series_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily target by product series (currently only TITAN, per the definition comment) for MDT branches. `fact_target_series_mdt` reads it. Same pattern as [dim_target_saleout_mdt](/dimension/dim_target_saleout_mdt.md) but at series grain.

Read by: [fact_target_series_mdt](/fact/fact_target_series_mdt.md).

# Grain and key

Monthly MDS rows de-duplicated per `(BranchCode, SeriesCode, Year, Month)` (latest `updated_at`), expanded to one row per calendar day. SK ordered by TargetDate, BranchCodeMdt, SeriesCode. Reserved row `TargetSeriesMdtSK = -1` (BranchCodeMdt 'NotBranch', SeriesCode 'NotSeries', SeriesName 'ไม่ระบุซีรีส์', NULL date and amounts). Partitioned by TargetDate.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetSeriesMdtSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by TargetDate, BranchCodeMdt, SeriesCode; -1 for the reserved row. Regenerated every run. |
| `BranchMdtSK` | INT64 | SK from dim_sales_branch_mdt joined on BranchCodeMdt (leading `GH_` rewritten to `GB_`); -1 when not found. |
| `SeriesSK` | INT64 | SK from [dim_product_series](/dimension/dim_product_series.md) by SeriesCode; unknown codes fall back to the OTHERS series (code 999999), or -1 if that row is missing. Regenerated daily like all full-rebuild SKs. |
| `StoreCode` | STRING | Store chain code from dim_sales_branch_mdt (NULL if unmatched); 'NotStore' on the -1 row. |
| `BranchCodeMdt` | STRING | MDT branch code from the target file; 'NotBranch' on the -1 row. |
| `SeriesCode` | STRING | Series code from the target file (trimmed); 'NotSeries' on the -1 row. It keeps the original code even when SeriesSK maps to OTHERS. |
| `SeriesName` | STRING | Series name from the target file; 'ไม่ระบุซีรีส์' on the -1 row. |
| `TargetDate` | DATE | Calendar day the daily target applies to; partition column; NULL on the -1 row. |
| `TargetYear` | INT64 | Year of the monthly target row. |
| `TargetMonth` | INT64 | Month (1-12) of the monthly target row. |
| `DaysInMonth` | INT64 | Calendar days in the target month; divisor for Amt and Qty. |
| `Amt` | FLOAT64 | Daily target amount = monthly `Value` / DaysInMonth (FLOAT64); NULL on the -1 row. |
| `Qty` | FLOAT64 | Daily target quantity = monthly `Quantity` / DaysInMonth (FLOAT64); NULL on the -1 row. |
| `MdsID` | STRING | `id` of the source row in `mds_data_mdt_sales_target_by_series`; NULL on the -1 row. |

# How it is built

- Definition: `definitions/dimension/dim_target_series_mdt.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `TargetSeriesMdtSK`.
- Storage options: `{"partitionBy": "TargetDate", "clusterBy": ["BranchMdtSK", "SeriesSK"]}`.
- Reads: `mds_dataset.mds_data_mdt_sales_target_by_series` (master data loaded outside this repo), [dimension_table.dim_product_series](/dimension/dim_product_series.md), [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md).
- Full daily rebuild (`type: "table"`), tags `dimension_daily` and `saleout_daily`; partitioned by TargetDate, clustered by BranchMdtSK, SeriesSK. Reads `mds_data_mdt_sales_target_by_series`, dim_sales_branch_mdt and dim_product_series.
- Approximate size (BigQuery metadata, 2026-10-31): 42,217 rows, 5.7 MB.

# Examples

Series target by month.

```sql
SELECT TargetYear, TargetMonth, SeriesCode, SUM(Amt) AS target_amt, SUM(Qty) AS target_qty
FROM `databuffet-nonprd.dimension_table.dim_target_series_mdt`
WHERE TargetDate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 90 DAY)
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
```

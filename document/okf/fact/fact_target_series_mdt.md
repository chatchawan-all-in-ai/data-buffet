---
type: BigQuery Table
title: "fact_target_series_mdt"
description: "One row = the daily target quantity of one MDT branch for one product series on one date."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_target_series_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_target_series_mdt
tags: ["fact", "fact_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_target_series_mdt.sqlx"
    title: "Dataform definition (fact/fact_target_series_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily series-level targets for modern trade from [dim_target_series_mdt](/dimension/dim_target_series_mdt.md), with branch, zone and as-at-date region/manager/director SKs; same pattern as [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md). BI compares it with sell-out via the product attribute SeriesSK (series names that do not match go to OTHERS). No other table in the repo reads it.

Used by / context: used by nothing else in the repo.

# Grain and key

One row per (`target_date`, `branch_code`, `series_code`) (uniqueKey). Monthly targets are split equally over the days of the month; NULL `TargetDate` rows are excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `target_date` | DATE | Date the daily target applies to (partition column); rows without a date are dropped. |
| `store_code` | STRING | Retail-chain (store) code: HP, MH, BT, GB, TW or DH, set per chain feed in the curated_saleout_mdt build; joins dim_region.RegionID for the region sets. |
| `branch_sk` | INT64 | Surrogate key `BranchMdtSK` of [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) carried from the target dim; -1 when unmatched. |
| `zone_sk` | INT64 | Surrogate key `ZoneMdtSK` of the branch's zone, taken from dim_sales_branch_mdt; -1 when unmatched. |
| `series_sk` | INT64 | Surrogate key `SeriesSK` of the product series, from dim_target_series_mdt; -1 if none. |
| `region_sk` | INT64 | `RegionSK` of [dim_region](/dimension/dim_region.md) valid on the row date (`store_code = RegionID`, date between StartDate and EndDate): the 'Region Transaction' value at the time, not the current one; -1 if none. |
| `region_manager_sk` | INT64 | `RegionManagerSK` of [dim_region_manager](/dimension/dim_region_manager.md) valid on the row date (not current); -1 if none. |
| `director_sk` | INT64 | `DirectorSK` of [dim_director](/dimension/dim_director.md) valid on the row date, reached via dim_region.DirectorID; -1 if none. |
| `series_code` | STRING | Product series code of the target. |
| `series_name` | STRING | Product series name. |
| `target_amt` | FLOAT64 | Daily target amount. |
| `target_qty` | FLOAT64 | Daily target quantity. |
| `target_year` | INT64 | Year of the target month. |
| `target_month` | INT64 | Month number of the target. |
| `days_in_month` | INT64 | Days in the target month; the monthly target is split equally across all days, so `target_amt * days_in_month` = the original monthly target. |
| `branch_code` | STRING | Branch code from MDS (`BranchCodeMdt`), degenerate, for tracing when branch_sk = -1. |
| `mds_id` | STRING | MDS row id of the target (trace column back to the MDS master). |

# How it is built

- Definition: `definitions/fact/fact_target_series_mdt.sqlx` (`type: "table"`, tags `fact_daily`, `saleout_daily`).
- `uniqueKey`: `target_date`, `branch_code`, `series_code`.
- Storage options: `{"partitionBy": "target_date", "clusterBy": ["store_code", "branch_sk", "series_sk"]}`.
- Reads: [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_target_series_mdt](/dimension/dim_target_series_mdt.md), [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md).
- Refresh: full daily rebuild (`type: "table"`, tags `fact_daily` and `saleout_daily`, partition `target_date`, cluster `store_code, branch_sk, series_sk`), after `dim_target_series_mdt`, `dim_sales_branch_mdt`, `dim_region`, `dim_region_manager`, `dim_director`.
- Approximate size (BigQuery metadata, 2026-10-31): 42,216 rows, 6.6 MB.

# Examples

Monthly target quantity by series.
```sql
SELECT series_code, series_name, SUM(target_qty) AS target_qty
FROM `databuffet-nonprd.fact_table.fact_target_series_mdt`
WHERE target_year = 2026 AND target_month = 10
GROUP BY series_code, series_name ORDER BY target_qty DESC;
```
Target quantity per branch for the month to date.
```sql
SELECT branch_sk, SUM(target_qty) AS target_qty
FROM `databuffet-nonprd.fact_table.fact_target_series_mdt`
WHERE target_date BETWEEN DATE '2026-10-01' AND CURRENT_DATE('Asia/Bangkok')
GROUP BY branch_sk;
```

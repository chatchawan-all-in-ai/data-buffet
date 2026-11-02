---
type: BigQuery Table
title: "fact_target_saleout_mdt"
description: "One row = the daily sell-out target of one MDT branch for one marketing group / sub-marketing / segment on one date."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_target_saleout_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_target_saleout_mdt
tags: ["fact", "fact_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_target_saleout_mdt.sqlx"
    title: "Dataform definition (fact/fact_target_saleout_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily sell-out targets for modern trade at marketing-group level (not per product), coming from [dim_target_saleout_mdt](/dimension/dim_target_saleout_mdt.md) (MDS target master) with branch, zone and as-at-date region/manager/director SKs. BI compares sell-out rolled up to MarketingGroupID against it. Used by `view_fact_target_pc_mdt` and `view_fact_target_section_mdt`.

Used by / context: used by [fact_view.view_fact_target_pc_mdt](/view/fact_view/view_fact_target_pc_mdt.md), [fact_view.view_fact_target_section_mdt](/view/fact_view/view_fact_target_section_mdt.md).

# Grain and key

One row per (`target_date`, `branch_code`, `marketing_group_id`, `sub_marketing_id`, `segment_id`) (uniqueKey). Monthly targets are divided equally over the days of the month. Rows with NULL `TargetDate` (the dim's unknown row) are excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `target_date` | DATE | Date the daily target applies to (partition column); rows without a date are dropped. |
| `store_code` | STRING | Retail-chain (store) code: HP, MH, BT, GB, TW or DH, set per chain feed in the curated_saleout_mdt build; joins dim_region.RegionID for the region sets. |
| `branch_sk` | INT64 | Surrogate key `BranchMdtSK` of [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) carried from the target dim; -1 when unmatched. |
| `zone_sk` | INT64 | Surrogate key `ZoneMdtSK` of the branch's zone, taken from dim_sales_branch_mdt; -1 when unmatched. |
| `product_mkt_sk` | INT64 | `ProductMktSK` of [dim_product_mkt](/dimension/dim_product_mkt.md) for the marketing group from the target dim; -1 if none. |
| `region_sk` | INT64 | `RegionSK` of [dim_region](/dimension/dim_region.md) valid on the row date (`store_code = RegionID`, date between StartDate and EndDate): the 'Region Transaction' value at the time, not the current one; -1 if none. |
| `region_manager_sk` | INT64 | `RegionManagerSK` of [dim_region_manager](/dimension/dim_region_manager.md) valid on the row date (not current); -1 if none. |
| `director_sk` | INT64 | `DirectorSK` of [dim_director](/dimension/dim_director.md) valid on the row date, reached via dim_region.DirectorID; -1 if none. |
| `marketing_group_id` | STRING | Marketing group code of the target (key to roll sales up to). |
| `marketing_group_name` | STRING | Marketing group name. |
| `sub_marketing_id` | STRING | Sub-marketing group code. |
| `sub_marketing_name` | STRING | Sub-marketing group name. |
| `segment_id` | STRING | Segment code. |
| `segment_name` | STRING | Segment name. |
| `target_amt` | FLOAT64 | Daily target amount (THB). |
| `target_qty` | FLOAT64 | Daily target quantity. |
| `target_year` | INT64 | Year of the target month. |
| `target_month` | INT64 | Month number of the target. |
| `days_in_month` | INT64 | Days in the target month; the monthly target is split equally across all days, so `target_amt * days_in_month` = the original monthly target. |
| `branch_code` | STRING | Branch code from MDS (`BranchCodeMdt`), degenerate, for tracing when branch_sk = -1. |
| `mds_id` | STRING | MDS row id of the target (trace column back to the MDS master). |

# How it is built

- Definition: `definitions/fact/fact_target_saleout_mdt.sqlx` (`type: "table"`, tags `fact_daily`, `saleout_daily`).
- `uniqueKey`: `target_date`, `branch_code`, `marketing_group_id`, `sub_marketing_id`, `segment_id`.
- Storage options: `{"partitionBy": "target_date", "clusterBy": ["store_code", "branch_sk", "marketing_group_id"]}`.
- Reads: [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_target_saleout_mdt](/dimension/dim_target_saleout_mdt.md), [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md).
- Refresh: full daily rebuild (`type: "table"`, tags `fact_daily` and `saleout_daily`, partition `target_date`, cluster `store_code, branch_sk, marketing_group_id`), after `dim_target_saleout_mdt`, `dim_sales_branch_mdt`, `dim_region`, `dim_region_manager`, `dim_director`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,044,467 rows, 192.5 MB.

# Examples

Monthly target amount per marketing group.
```sql
SELECT marketing_group_id, marketing_group_name, SUM(target_amt) AS target_amt
FROM `databuffet-nonprd.fact_table.fact_target_saleout_mdt`
WHERE target_year = 2026 AND target_month = 10
GROUP BY marketing_group_id, marketing_group_name;
```
Target for one chain up to today (Asia/Bangkok).
```sql
SELECT SUM(target_amt) AS target_to_date
FROM `databuffet-nonprd.fact_table.fact_target_saleout_mdt`
WHERE store_code = 'GB' AND target_date BETWEEN DATE '2026-10-01' AND CURRENT_DATE('Asia/Bangkok');
```

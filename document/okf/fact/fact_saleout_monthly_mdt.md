---
type: BigQuery Table
title: "fact_saleout_monthly_mdt"
description: "One row = one chain (store_code) x branch x sales channel x product x month_date total of sell-out as reported by the chain monthly (or collapsed from the daily feed)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_saleout_monthly_mdt&page=table"
tags: ["fact", "saleout", "fact_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_saleout_monthly_mdt.sqlx"
    title: "Dataform definition (fact/fact_saleout_monthly_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Monthly sell-out fact for modern trade, built from `curated_saleout_monthly_mdt`, which picks per (month, chain) the best source: chain closing file > BI file > collapsed daily feed. It is used to compare against the daily [fact_saleout_mdt](/fact/fact_saleout_mdt.md) and feeds `view_fact_saleout_pc_mdt`. It has the same dimension SKs as fact_saleout_mdt.

Used by / context: used by [fact_view.view_fact_saleout_pc_mdt](/view/fact_view/view_fact_saleout_pc_mdt.md).

# Grain and key

Uniqueness key: (`month_date`, `store_code`, `branch_code`, `sales_channel`, `product_code`). Mixed grain: for the current (in-progress) month `month_date` is the daily sale date; for closed months it is the month-end date (comment in SQL: running month = daily, closed month = one block).

# Schema

| Column | Type | Description |
|---|---|---|
| `month_date` | DATE | Month key (partition column): daily date for the current month, month-end date for closed months. Group by DATE_TRUNC(month_date, MONTH). |
| `store_code` | STRING | Retail-chain (store) code as sent by the chain (e.g. HP/MH/BT/GB/TW/DH, inferred from curated docs); joins dim_region.RegionID for the region sets. |
| `branch_code` | STRING | Branch code/name as sent by the chain (trimmed when matched). |
| `sales_channel` | STRING | Sales channel from the source, '-' when the source grain has none. |
| `product_code` | STRING | Product code as the chain sent it (leading zeros stripped for the dim match). |
| `product_name` | STRING | Product name as sent by the chain (from curated_saleout_monthly_mdt). |
| `branch_sk` | INT64 | Surrogate key `BranchMdtSK` of [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) (match on store code + branch code); -1 when the branch is not in the dimension. |
| `zone_sk` | INT64 | Surrogate key `ZoneMdtSK` of the branch's zone, taken from dim_sales_branch_mdt; -1 when unmatched. |
| `product_mdt_sk` | INT64 | Surrogate key `ProductMdtSK` of [dim_product_mdt](/dimension/dim_product_mdt.md) (match on product code with leading zeros removed); -1 when the product is unknown. |
| `product_sk` | INT64 | `ProductSK` carried from dim_product_mdt (link to the MAC5 product master where mapped); -1 when unknown. |
| `product_mkt_sk` | INT64 | Surrogate key `ProductMktSK` of [dim_product_mkt](/dimension/dim_product_mkt.md) (marketing group of the product); products with no group fall back to the 'Waiting Master' group (MarketingGroupID '999'), found by ID because SKs change daily; -1 if that group is missing. |
| `report_sk` | INT64 | Surrogate key `ReportSK` of [dim_report](/dimension/dim_report.md) by (store, marketing group), falling back to the store's 'Other' line; -1 if none. |
| `region_sk` | INT64 | `RegionSK` of [dim_region](/dimension/dim_region.md) valid on the row date (`store_code = RegionID`, date between StartDate and EndDate): the 'Region Transaction' value at the time, not the current one; -1 if none. |
| `region_manager_sk` | INT64 | `RegionManagerSK` of [dim_region_manager](/dimension/dim_region_manager.md) valid on the row date (not current); -1 if none. |
| `director_sk` | INT64 | `DirectorSK` of [dim_director](/dimension/dim_director.md) valid on the row date, reached via dim_region.DirectorID; -1 if none. |
| `sale_qty` | FLOAT64 | Quantity sold in the period, FLOAT64 (from curated_saleout_monthly_mdt). |
| `sale_amount` | FLOAT64 | Sales amount in the period (THB), from curated_saleout_monthly_mdt. |
| `asatdate` | DATE | CURRENT_DATE('Asia/Bangkok') at build time. |

# How it is built

- Definition: `definitions/fact/fact_saleout_monthly_mdt.sqlx` (`type: "table"`, tags `fact_daily`, `saleout_daily`).
- `uniqueKey`: `month_date`, `store_code`, `branch_code`, `sales_channel`, `product_code`.
- Storage options: `{"partitionBy": "month_date", "clusterBy": ["store_code", "branch_sk", "product_mdt_sk"]}`.
- Reads: [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_report](/dimension/dim_report.md), [dimension_table.dim_product_mdt](/dimension/dim_product_mdt.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_director](/dimension/dim_director.md), [curated_saleout_mdt.curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md).
- Refresh: full daily rebuild (`type: "table"`, tags `fact_daily` and `saleout_daily`, partition `month_date`, cluster `store_code, branch_sk, product_mdt_sk`) because the curated source changes daily; after the MDT dims; re-run in `saleout_morning`.
- Approximate size (BigQuery metadata, 2026-10-31): 373,203 rows, 78.9 MB.

# Examples

Monthly sell-out per chain (correct for mixed grain).
```sql
SELECT store_code, DATE_TRUNC(month_date, MONTH) AS month, SUM(sale_qty) AS qty, SUM(sale_amount) AS amount
FROM `databuffet-nonprd.fact_table.fact_saleout_monthly_mdt`
WHERE DATE_TRUNC(month_date, MONTH) = DATE '2026-10-01'
GROUP BY store_code, month;
```
Top products of a chain for a month.
```sql
SELECT product_code, product_name, SUM(sale_amount) AS amount
FROM `databuffet-nonprd.fact_table.fact_saleout_monthly_mdt`
WHERE store_code = 'TW' AND DATE_TRUNC(month_date, MONTH) = DATE '2026-09-01'
GROUP BY product_code, product_name ORDER BY amount DESC LIMIT 20;
```

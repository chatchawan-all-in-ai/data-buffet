---
type: BigQuery Table
title: "fact_saleout_mdt"
description: "One row = one sell-out (sale or return) document-type total per sale date, store (chain), branch and product from the modern-trade chains' daily feeds."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_saleout_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_saleout_mdt
tags: ["fact", "saleout", "fact_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_saleout_mdt.sqlx"
    title: "Dataform definition (fact/fact_saleout_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Modern-trade sell-out fact: daily sales and returns reported by the retail chains (HomePro, Boonthavorn, Global House, Thai Watsadu, DoHome etc.), unioned in `curated_saleout_mdt`, with surrogate keys to the MDT branch/product/marketing/report/region dimensions. It answers what each chain sold per branch, product and day. Used by `view_fact_stock_nonmove_mdt` (non-moving stock) and BI sell-out views. It uses the separate MDT product universe, not the MAC5 product dimension.

Used by / context: used by [fact_view.view_fact_stock_nonmove_mdt](/view/fact_view/view_fact_stock_nonmove_mdt.md).

# Grain and key

One row per (`sale_date`, `store_code`, `branch_code`, `product_code`, `doc_type`) - the uniqueKey, taken from `curated_saleout_mdt`. `doc_type` is 'SALE' or 'RETURN' (returns typically carry negative amounts). Excluded: store 'GB' rows whose marketing segment is 00221 or 00222 (to match the GB BI file).

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Date of the sale (partition column). For BT, spread evenly over the covered range when the feed gives a date range. |
| `store_code` | STRING | Retail-chain (store) code: HP, MH, BT, GB, TW or DH, set per chain feed in the curated_saleout_mdt build; joins dim_region.RegionID for the region sets. |
| `branch_sk` | INT64 | Surrogate key `BranchMdtSK` of [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) (match on store code + branch code); -1 when the branch is not in the dimension. |
| `zone_sk` | INT64 | Surrogate key `ZoneMdtSK` of the branch's zone, taken from dim_sales_branch_mdt; -1 when unmatched. |
| `product_mdt_sk` | INT64 | Surrogate key `ProductMdtSK` of [dim_product_mdt](/dimension/dim_product_mdt.md) (match on product code with leading zeros removed); -1 when the product is unknown. |
| `product_sk` | INT64 | `ProductSK` carried from dim_product_mdt (link to the MAC5 product master where mapped); -1 when unknown. |
| `product_mkt_sk` | INT64 | Surrogate key `ProductMktSK` of [dim_product_mkt](/dimension/dim_product_mkt.md) (marketing group of the product); products with no group fall back to the 'Waiting Master' group (MarketingGroupID '999'), found by ID because SKs change daily; -1 if that group is missing. |
| `report_sk` | INT64 | Surrogate key `ReportSK` of [dim_report](/dimension/dim_report.md): the report line for (store, marketing group), falling back to the store's 'Other' line; -1 if none. |
| `region_sk` | INT64 | `RegionSK` of [dim_region](/dimension/dim_region.md) valid on the row date (`store_code = RegionID`, date between StartDate and EndDate): the 'Region Transaction' value at the time, not the current one; -1 if none. |
| `region_manager_sk` | INT64 | `RegionManagerSK` of [dim_region_manager](/dimension/dim_region_manager.md) valid on the row date (not current); -1 if none. |
| `director_sk` | INT64 | `DirectorSK` of [dim_director](/dimension/dim_director.md) valid on the row date, reached via dim_region.DirectorID; -1 if none. |
| `doc_type` | STRING | 'SALE' or 'RETURN' (from the chain, or derived from the sign/flag). |
| `doc_type_source` | STRING | 'SOURCE' when the chain sent the document type, 'DERIVED' when the build derived it (from curated_saleout_mdt). |
| `sale_qty` | INT64 | Quantity sold (negative or flagged return when doc_type RETURN), from curated_saleout_mdt. |
| `sale_amount` | FLOAT64 | Sales amount, from curated_saleout_mdt (currency THB; sign negative on returns). |
| `days_covered` | INT64 | Number of days the source row covered (1 = exact day; >1 when the chain sent a range that was spread, e.g. BT). |
| `date_is_estimated` | BOOL | TRUE when `days_covered > 1` (sale date is estimated), else FALSE. |
| `branch_code` | STRING | Branch code/name exactly as the chain sent it (degenerate; format varies per chain). |
| `product_code` | STRING | Product code as the chain sent it (may have leading zeros; matched to dim_product_mdt after LTRIM of '0'). |
| `asatdate` | DATE | Extract/snapshot date carried from curated_saleout_mdt. |

# How it is built

- Definition: `definitions/fact/fact_saleout_mdt.sqlx` (`type: "table"`, tags `fact_daily`, `saleout_daily`).
- `uniqueKey`: `sale_date`, `store_code`, `branch_code`, `product_code`, `doc_type`.
- Storage options: `{"partitionBy": "sale_date", "clusterBy": ["store_code", "branch_sk", "product_mdt_sk"]}`.
- Reads: [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_report](/dimension/dim_report.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_director](/dimension/dim_director.md), [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md), [dimension_table.dim_product_mdt](/dimension/dim_product_mdt.md).
- Refresh: full daily rebuild (`type: "table"`, tags `fact_daily` and `saleout_daily`, uniqueKey above, partition `sale_date`, cluster `store_code, branch_sk, product_mdt_sk`), after the MDT dims (`dim_sales_branch_mdt`, `dim_product_mdt`, `dim_product_mkt`, `dim_report`, `dim_region`, `dim_region_manager`, `dim_director`); also re-run in workflow `saleout_morning` 08:55.

# Examples

Sell-out amount per chain per month (sales and returns net).
```sql
SELECT store_code, DATE_TRUNC(sale_date, MONTH) AS month, SUM(sale_qty) AS qty, SUM(sale_amount) AS amount
FROM `databuffet-nonprd.fact_table.fact_saleout_mdt`
WHERE sale_date >= DATE '2026-01-01'
GROUP BY store_code, month ORDER BY month, store_code;
```
Exact-date sales only (spread-over-range estimates excluded).
```sql
SELECT sale_date, branch_sk, SUM(sale_amount) AS amount
FROM `databuffet-nonprd.fact_table.fact_saleout_mdt`
WHERE sale_date >= DATE '2026-10-01' AND NOT date_is_estimated
GROUP BY sale_date, branch_sk;
```

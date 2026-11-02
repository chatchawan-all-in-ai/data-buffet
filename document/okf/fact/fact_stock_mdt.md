---
type: BigQuery Table
title: "fact_stock_mdt"
description: "One row = on-hand (and on-order) stock of one product at one chain branch on one stock date."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_stock_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_stock_mdt
tags: ["fact", "saleout", "fact_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_stock_mdt.sqlx"
    title: "Dataform definition (fact/fact_stock_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily stock snapshot of the modern-trade chains' branches (on-hand quantity, on-hand cost value for BT only, on-order quantity for TW only), keyed to the MDT branch/product dimensions. It answers how much stock each chain holds per branch/product and supports non-moving-stock analysis (`view_fact_stock_nonmove_mdt`) and monthly roll-up in [fact_stock_mdt_monthly](/fact/fact_stock_mdt_monthly.md).

Used by / context: used by [fact_table.fact_stock_mdt_monthly](/fact/fact_stock_mdt_monthly.md), [fact_view.view_fact_stock_nonmove_mdt](/view/fact_view/view_fact_stock_nonmove_mdt.md).

# Grain and key

One row per (`stock_date`, `store_code`, `branch_code`, `product_code`) (the uniqueKey), from `curated_stock_mdt`.

# Schema

| Column | Type | Description |
|---|---|---|
| `stock_date` | DATE | Date of the stock snapshot (partition column). |
| `store_code` | STRING | Retail-chain (store) code: HP, MH, BT, GB, TW or DH, set per chain feed in the curated_saleout_mdt build; joins dim_region.RegionID for the region sets. |
| `branch_sk` | INT64 | Surrogate key `BranchMdtSK` of [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) (match on store code + branch code); -1 when the branch is not in the dimension. |
| `zone_sk` | INT64 | Surrogate key `ZoneMdtSK` of the branch's zone, taken from dim_sales_branch_mdt; -1 when unmatched. |
| `product_mdt_sk` | INT64 | Surrogate key `ProductMdtSK` of [dim_product_mdt](/dimension/dim_product_mdt.md) (match on product code with leading zeros removed); -1 when the product is unknown. |
| `product_sk` | INT64 | `ProductSK` carried from dim_product_mdt (link to the MAC5 product master where mapped); -1 when unknown. |
| `product_mkt_sk` | INT64 | `ProductMktSK` of [dim_product_mkt](/dimension/dim_product_mkt.md) carried from dim_product_mdt; -1 when unknown (no Waiting-group fallback here). |
| `onhand_qty` | INT64 | On-hand quantity (from curated_stock_mdt). |
| `onhand_amt` | FLOAT64 | On-hand value at cost (not selling price); only BT sends it, NULL for TW. |
| `onorder_qty` | INT64 | Quantity on order; only TW sends it, NULL for BT. |
| `branch_code` | STRING | Branch code as the chain sent it (degenerate). |
| `product_code` | STRING | Product code as the chain sent it (degenerate; leading zeros stripped for the dim match). |
| `asatdate` | DATE | Extract/snapshot date carried from curated_stock_mdt. |

# How it is built

- Definition: `definitions/fact/fact_stock_mdt.sqlx` (`type: "table"`, tags `fact_daily`, `saleout_daily`).
- `uniqueKey`: `stock_date`, `store_code`, `branch_code`, `product_code`.
- Storage options: `{"partitionBy": "stock_date", "clusterBy": ["store_code", "branch_sk", "product_mdt_sk"]}`.
- Reads: [curated_saleout_mdt.curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md), [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md), [dimension_table.dim_product_mdt](/dimension/dim_product_mdt.md).
- Refresh: full daily rebuild (`type: "table"`, tags `fact_daily` and `saleout_daily`, partition `stock_date`, cluster `store_code, branch_sk, product_mdt_sk`), after `dim_sales_branch_mdt` and `dim_product_mdt`; re-run in `saleout_morning`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,310,751 rows, 170.3 MB.

# Examples

Latest on-hand quantity per chain.
```sql
WITH latest_stock AS (
  SELECT store_code, stock_date, onhand_qty,
         MAX(stock_date) OVER (PARTITION BY store_code) AS latest_stock_date
  FROM `databuffet-nonprd.fact_table.fact_stock_mdt`
)
SELECT store_code, SUM(onhand_qty) AS onhand_qty
FROM latest_stock
WHERE stock_date = latest_stock_date
GROUP BY store_code;
```
Stock history of one product code across branches.
```sql
SELECT stock_date, branch_sk, onhand_qty
FROM `databuffet-nonprd.fact_table.fact_stock_mdt`
WHERE product_mdt_sk = 12345 AND stock_date >= DATE '2026-10-01';
```

---
type: BigQuery Table
title: "fact_stock_mdt_monthly"
description: "One row = the stock position of one product at one chain branch on the last usable stock date of a month for that chain."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_stock_mdt_monthly&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_stock_mdt_monthly
tags: ["fact", "fact_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_stock_mdt_monthly.sqlx"
    title: "Dataform definition (fact/fact_stock_mdt_monthly.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Month-end stock snapshot derived from [fact_stock_mdt](/fact/fact_stock_mdt.md): for each chain and month it takes the last day on which that chain has non-empty data and returns that day's stock for every branch/product. It answers month-end stock by branch/product.

Read by: none in this repository.

# Grain and key

One row = the stock position of one product at one chain branch on the last usable stock date of a month for that chain: key (`month_end`, `store_code`, `branch_code`, `product_code`) - the uniqueKey. `snapshot_date` is the actual stock date used (the chain's last day in the month with SUM(onhand_qty) <> 0). `month_end` is the calendar month-end for closed months and, for the current month, the latest snapshot date across all chains.

# Schema

| Column | Type | Description |
|---|---|---|
| `month_end` | DATE | Month label: calendar month-end (LAST_DAY) for closed months; the latest snapshot date across all chains for the current month. Partition column. |
| `snapshot_date` | DATE | Actual stock date of the chain used for this row. |
| `is_month_end` | BOOL | TRUE when the month is closed (before the current month), FALSE for the current month (value is the latest, not month-end). |
| `store_code` | STRING | Retail-chain (store) code carried from `fact_stock_mdt` ('BT' or 'TW'). |
| `branch_sk` | INT64 | Surrogate key `BranchMdtSK` of [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) (match on store code + branch code); -1 when the branch is not in the dimension. |
| `zone_sk` | INT64 | Surrogate key `ZoneMdtSK` of the branch's zone, taken from dim_sales_branch_mdt; -1 when unmatched. |
| `product_mdt_sk` | INT64 | Surrogate key `ProductMdtSK` of [dim_product_mdt](/dimension/dim_product_mdt.md) (match on product code with leading zeros removed); -1 when the product is unknown. |
| `product_sk` | INT64 | `ProductSK` carried from dim_product_mdt (link to the MAC5 product master where mapped); -1 when unknown. |
| `product_mkt_sk` | INT64 | `ProductMktSK` carried from fact_stock_mdt; -1 when unknown. |
| `onhand_qty` | INT64 | On-hand quantity on snapshot_date (from fact_stock_mdt). |
| `onhand_amt` | FLOAT64 | On-hand cost value; only BT, NULL for TW. |
| `onorder_qty` | INT64 | On-order quantity; only TW, NULL for BT. |
| `branch_code` | STRING | Branch code as sent by the chain (degenerate). |
| `product_code` | STRING | Product code as sent by the chain (degenerate). |
| `asatdate` | DATE | asatdate carried from fact_stock_mdt. |

# How it is built

- Definition: `definitions/fact/fact_stock_mdt_monthly.sqlx` (`type: "table"`, tags `fact_daily`, `saleout_daily`).
- `uniqueKey`: `month_end`, `store_code`, `branch_code`, `product_code`.
- Storage options: `{"partitionBy": "month_end", "clusterBy": ["store_code", "branch_sk", "product_mdt_sk"]}`.
- Reads: [fact_table.fact_stock_mdt](/fact/fact_stock_mdt.md).
- Refresh: full daily rebuild (`type: "table"`, tags `fact_daily` and `saleout_daily`, partition `month_end`, cluster `store_code, branch_sk, product_mdt_sk`), after `fact_stock_mdt`.

# Examples

Month-end on-hand quantity per chain for closed months.
```sql
SELECT month_end, store_code, SUM(onhand_qty) AS onhand_qty
FROM `databuffet-nonprd.fact_table.fact_stock_mdt_monthly`
WHERE is_month_end
GROUP BY month_end, store_code ORDER BY month_end, store_code;
```
Which actual dates each chain's current month value comes from.
```sql
SELECT store_code, month_end, MAX(snapshot_date) AS snapshot_date
FROM `databuffet-nonprd.fact_table.fact_stock_mdt_monthly`
WHERE NOT is_month_end
GROUP BY store_code, month_end;
```

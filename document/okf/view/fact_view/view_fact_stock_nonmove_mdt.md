---
type: BigQuery View
title: "view_fact_stock_nonmove_mdt"
description: "One row = the latest in-stock snapshot (onhand_qty > 0) of one product at one chain branch, with its last sale date and a slow/non-moving status bucket."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_stock_nonmove_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_stock_nonmove_mdt
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_stock_nonmove_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_stock_nonmove_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Non-moving stock report for modern-trade chains. It takes the latest snapshot per (chain, branch, product) from [fact_stock_mdt](/fact/fact_stock_mdt.md), keeps only items still on hand, and joins the last time that item sold in [fact_saleout_mdt](/fact/fact_saleout_mdt.md), then buckets the age.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per (store_code, branch_code, product_code): `latest_stock` keeps `ROW_NUMBER() ... ORDER BY stock_date DESC = 1`, then `WHERE onhand_qty > 0`. The sales aggregate is also per (store, branch, product), so the LEFT JOIN is 1:1.

# Schema

| Column | Type | Description |
|---|---|---|
| `stock_date` | DATE | Date of the latest stock snapshot of this (store, branch, product) in `fact_stock_mdt`; each chain delivers files on its own schedule so dates can differ between rows. |
| `store_code` | STRING | Modern-trade chain code. |
| `branch_code` | STRING | Branch code as sent by the chain. |
| `branch_sk` | INT64 | SK of `dim_sales_branch_mdt` (`-1` unknown). |
| `zone_sk` | INT64 | ZoneMdtSK of the branch (`-1` unknown). |
| `product_code` | STRING | Chain product code as sent. |
| `product_mdt_sk` | INT64 | SK of `dim_product_mdt` (`-1` unknown). |
| `product_sk` | INT64 | SK of `dim_product_master` (`-1` unknown). |
| `product_mkt_sk` | INT64 | SK of `dim_product_mkt` (`-1` unknown). |
| `onhand_qty` | INT64 | On-hand quantity at `stock_date`; always > 0 in this view. |
| `onhand_amt` | FLOAT64 | On-hand value (cost) at `stock_date`; only provided by BT per the fact comments, otherwise NULL/0. |
| `onorder_qty` | INT64 | On-order quantity; only provided by TW per the fact comments. |
| `last_sold_date` | DATE | Latest `sale_date` in `fact_saleout_mdt` with `sale_qty > 0` for the same (store, branch, product); NULL when never sold. |
| `days_since_last_sale` | INT64 | `DATE_DIFF(stock_date, last_sold_date, DAY)`, counted from the row's own stock date (not today); NULL when never sold. |
| `lifetime_sold_qty` | INT64 | Total positive `sale_qty` ever recorded for the (store, branch, product) in `fact_saleout_mdt` (returns excluded). |
| `lifetime_sold_amount` | FLOAT64 | Total `sale_amount` of the positive-quantity sale rows. |
| `move_status` | STRING | Movement bucket in Thai: `ไม่มีประวัติขาย` (never sold), `0-30 วัน`, `31-60 วัน`, `61-90 วัน`, `เกิน 90 วัน` (over 90 days) by days_since_last_sale. |
| `asatdate` | DATE | Load date of the stock row in `fact_stock_mdt`. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_stock_nonmove_mdt.sqlx` (`type: "view"`, tags `view`).
- Reads: [fact_table.fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_table.fact_stock_mdt](/fact/fact_stock_mdt.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `fact_stock_mdt` and `fact_saleout_mdt` (tags `fact_daily` + `saleout_daily`) being rebuilt first.

# Examples

On-hand quantity and value by chain and movement bucket.

```sql
SELECT store_code, move_status, COUNT(*) AS items, SUM(onhand_qty) AS onhand_qty
FROM `databuffet-nonprd.fact_view.view_fact_stock_nonmove_mdt`
GROUP BY store_code, move_status
ORDER BY store_code, move_status
```

Items on hand that have not sold for over 90 days or never sold.

```sql
SELECT store_code, branch_code, product_code, stock_date, onhand_qty, last_sold_date, days_since_last_sale
FROM `databuffet-nonprd.fact_view.view_fact_stock_nonmove_mdt`
WHERE move_status IN ('เกิน 90 วัน', 'ไม่มีประวัติขาย')
ORDER BY onhand_qty DESC
LIMIT 200
```

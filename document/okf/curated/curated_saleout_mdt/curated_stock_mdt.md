---
type: BigQuery Table
title: "curated_stock_mdt"
description: "One row = the on-hand stock of one product at one Boonthavorn (BT) or Thai Watsadu (TW) branch on one stock date."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_saleout_mdt&t=curated_stock_mdt&page=table"
tags: ["curated", "curated_saleout_mdt", "saleout", "curated_full", "saleout_daily", "SALEOUT_MDT"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/saleout_mdt/curated_stock_mdt.sqlx"
    title: "Dataform definition (curated/saleout_mdt/curated_stock_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily stock-on-hand snapshot per branch and product for the modern-trade (MDT) chains that send stock: BT (separate stock_by_branch file, stock date = its end_date) and TW (stock columns of the sales report). Feeds fact_stock_mdt and the product and branch dimensions dim_product_mdt and dim_sales_branch_mdt.

# Grain and key

One row per `stock_date`, `store_code` (BT or TW), `branch_code` and `product_code`. Each block is deduplicated so the key is unique: BT keeps the latest file per (branch, article, end_date); TW keeps one row per (asatdate, store, SKU) ordered by Last_Sold_Date, then Stock_On_Hand. There is no declared uniqueKey (rebuilt table).

# Schema

| Column | Type | Description |
|---|---|---|
| `stock_date` | DATE | Date the stock refers to. BT: end_date of the file. TW: the file's asatdate minus 1 day (assumed, not confirmed with the chain, to match BT's end_date = file day minus 1). |
| `store_code` | STRING | Chain code: 'BT' or 'TW'. |
| `branch_code` | STRING | Branch identifier: BT uses the Thai branch name, TW the full store string like '60001-CRC Thai Watsadu ...'. |
| `product_code` | STRING | BT: article_id. TW: SKU with leading zeros stripped (so it matches dim_product_mdt and TW sales). |
| `product_name` | STRING | Article name (BT article_name_th, TW Description). |
| `onhand_qty` | INT64 | Quantity on hand (BT ur_qty, TW Stock_On_Hand cast to INT64). |
| `onhand_amt` | FLOAT64 | Stock value. BT: ur_cost_amt, which is cost, not selling price. TW: always NULL (not sent). |
| `onorder_qty` | INT64 | Quantity on order (TW Stock_On_Order). BT: always NULL (not sent). |
| `asatdate` | DATE | Raw load date (partition date of the validated source row). |

# How it is built

- Definition: `definitions/curated/saleout_mdt/curated_stock_mdt.sqlx` (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`).
- Storage options: `{"partitionBy": "stock_date", "clusterBy": ["store_code", "branch_code", "product_code"]}`.
- Reads: [validated_saleout_mdt.stock_by_branch](/validated/validated_saleout_mdt/stock_by_branch.md), [validated_saleout_mdt.report_sale_subscription](/validated/validated_saleout_mdt/report_sale_subscription.md).
- Full rebuild each run (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`; depends on `curated_schema_saleout`); partitioned by `stock_date`, clustered by store_code, branch_code, product_code.
- Approximate size (BigQuery metadata, 2026-10-31): 1,310,751 rows, 241.4 MB.

# Examples

Latest stock date per chain, then the stock at that date.

```sql
SELECT store_code, branch_code, product_code, onhand_qty, onhand_amt
FROM `databuffet-nonprd.curated_saleout_mdt.curated_stock_mdt`
WHERE stock_date = (SELECT MAX(stock_date) FROM `databuffet-nonprd.curated_saleout_mdt.curated_stock_mdt` WHERE store_code = 'BT')
  AND store_code = 'BT'
```

Total quantity on hand by chain on one date.

```sql
SELECT store_code, SUM(onhand_qty) AS onhand_qty
FROM `databuffet-nonprd.curated_saleout_mdt.curated_stock_mdt`
WHERE stock_date = DATE '2026-10-20'
GROUP BY store_code
```

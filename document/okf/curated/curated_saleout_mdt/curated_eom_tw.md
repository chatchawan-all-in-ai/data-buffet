---
type: BigQuery Table
title: "curated_eom_tw"
description: "One row = the month-end sales total of one product at one Thai Watsadu (TW) store for one period, as reported by the chain."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_saleout_mdt&t=curated_eom_tw&page=table"
tags: ["curated", "curated_saleout_mdt", "saleout", "curated_full", "saleout_daily", "SALEOUT_MDT"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/saleout_mdt/curated_eom_tw.sqlx"
    title: "Dataform definition (curated/saleout_mdt/curated_eom_tw.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Closing (EOM) sales and stock report that Thai Watsadu sends itself (folder SO_MDT_EOM/TW), kept as the figure 'as reported by the chain' (TW closes on the 8th of the next month) and used as the CHAIN_FILE source of [curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md). Only rows with some sale are kept (pure stock lines dropped).

# Grain and key

One row per `month_date` (first day of the period, from the PERIOD column read from the file header), `branch_code` (full store string) and `product_code` (SKU without leading zeros). `store_code` is constant 'TW'. Declared `uniqueKey` is month_date, branch_code, product_code.

# Schema

| Column | Type | Description |
|---|---|---|
| `month_date` | DATE | First day of the period from the PERIOD header value (e.g. 2026-08 becomes 2026-08-01). Not Last_Sold_Date and not ASATDATE. |
| `store_code` | STRING | Chain code, constant 'TW'. |
| `branch_code` | STRING | Full store string such as '60001-CRC Thai Watsadu ...' (Store column), same convention as the daily feed. |
| `product_code` | STRING | SKU with leading zeros stripped (LTRIM), so it matches curated_saleout_mdt.product_code. |
| `product_name` | STRING | Product description (Description column). |
| `barcode_match` | STRING | Barcode (Barcode column, cleaned) for matching the product master. |
| `sale_qty` | INT64 | Sum of Sales_Qty for the key. |
| `sale_amount` | FLOAT64 | Sum of Sales_Amount for the key. |
| `asatdate` | DATE | Latest raw load date among the rows summed (the DAG run date, not the period). |

# How it is built

- Definition: `definitions/curated/saleout_mdt/curated_eom_tw.sqlx` (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`).
- `uniqueKey`: `month_date`, `branch_code`, `product_code`.
- Storage options: `{"partitionBy": "month_date", "clusterBy": ["branch_code", "product_code"]}`.
- Reads: [raw_saleout_mdt.eom_tw](/initial/raw_saleout_mdt/eom_tw.md).
- Full rebuild each run (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`; depends on `curated_schema_saleout` and `create_all_table_raw_saleout_mdt`); partitioned by `month_date`, clustered by branch_code, product_code. Reads raw `eom_tw` directly.
- Approximate size (BigQuery metadata, 2026-10-31): 4,352 rows, 868.6 KB.

# Examples

Month total per store for one period.

```sql
SELECT month_date, branch_code, SUM(sale_amount) AS amount
FROM `databuffet-nonprd.curated_saleout_mdt.curated_eom_tw`
WHERE month_date = DATE '2026-08-01'
GROUP BY month_date, branch_code
ORDER BY amount DESC
```

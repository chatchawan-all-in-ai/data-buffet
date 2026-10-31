---
type: BigQuery Table
title: "curated_eom_gb"
description: "One row = the month-end sales total of one product and document type (SALE or RETURN) at one Global House (GB) branch for one period, as reported by the chain."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_saleout_mdt&t=curated_eom_gb&page=table"
project_id: databuffet-nonprd
dataset_id: curated_saleout_mdt
table_id: curated_eom_gb
tags: ["curated", "curated_saleout_mdt", "saleout", "curated_full", "saleout_daily", "SALEOUT_MDT"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/saleout_mdt/curated_eom_gb.sqlx"
    title: "Dataform definition (curated/saleout_mdt/curated_eom_gb.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Closing (EOM) sales file that Global House (GB) sends itself (folder SO_MDT_EOM/GB), kept as 'the figure reported by the chain' to compare with the daily feed and as the CHAIN_FILE source of [curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md). The bill lines of the file are rolled up to month level.

# Grain and key

One row per `month_date` (first day of the period, from the Sale_Date column), `branch_code`, `product_code` (13-digit barcode) and `doc_type`. `store_code` is constant 'GB'. Declared `uniqueKey` is month_date, branch_code, product_code, doc_type.

# Schema

| Column | Type | Description |
|---|---|---|
| `month_date` | DATE | First day of the month of the Sale_Date column (DATE_TRUNC; the period is taken from the data, never from ASATDATE). |
| `store_code` | STRING | Chain code, constant 'GB' (Global House). |
| `branch_code` | STRING | Branch code (Branch_Code, cleaned). |
| `branch_name` | STRING | Branch name (Branch_Name); one value per key (ANY_VALUE). |
| `product_code` | STRING | Product code (Product_Code); numeric only (13-digit barcode); non-numeric codes (freight revenue) and 3 Hitachi water-pump barcodes are excluded. |
| `product_name` | STRING | Product name (Product_Name); one value per key (ANY_VALUE). |
| `doc_type` | STRING | Document type as sent by the chain (Type column): SALE or RETURN. |
| `sale_qty` | INT64 | Sum of Sale_Quantity for the key; negative for returns. |
| `sale_amount` | FLOAT64 | Sum of Sale_Amount, parsed from a dirty string (thousands commas and a leading apostrophe on return rows are stripped); returns are negative. |
| `asatdate` | DATE | Latest raw load date among the rows summed (the DAG run date, not the period). |

# How it is built

- Definition: `definitions/curated/saleout_mdt/curated_eom_gb.sqlx` (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`).
- `uniqueKey`: `month_date`, `branch_code`, `product_code`, `doc_type`.
- Storage options: `{"partitionBy": "month_date", "clusterBy": ["branch_code", "product_code"]}`.
- Reads: [raw_saleout_mdt.eom_gb](/initial/raw_saleout_mdt/eom_gb.md).
- Full rebuild each run (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`; depends on `curated_schema_saleout` and `create_all_table_raw_saleout_mdt`); partitioned by `month_date`, clustered by branch_code, product_code. Reads raw `eom_gb` directly.
- Approximate size (BigQuery metadata, 2026-10-31): 3,166 rows, 768.7 KB.

# Examples

Month totals by document type for one period.

```sql
SELECT month_date, doc_type, SUM(sale_amount) AS amount, SUM(sale_qty) AS qty
FROM `databuffet-nonprd.curated_saleout_mdt.curated_eom_gb`
WHERE month_date = DATE '2026-09-01'
GROUP BY month_date, doc_type
```

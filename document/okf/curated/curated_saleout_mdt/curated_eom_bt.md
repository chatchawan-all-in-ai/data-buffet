---
type: BigQuery Table
title: "curated_eom_bt"
description: "One row = the month-end sales total of one product at one Boonthavorn (BT) branch for one closed period, as reported by the chain itself."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_saleout_mdt&t=curated_eom_bt&page=table"
project_id: databuffet-nonprd
dataset_id: curated_saleout_mdt
table_id: curated_eom_bt
tags: ["curated", "curated_saleout_mdt", "saleout", "curated_full", "saleout_daily", "SALEOUT_MDT"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/saleout_mdt/curated_eom_bt.sqlx"
    title: "Dataform definition (curated/saleout_mdt/curated_eom_bt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Closing (end-of-month, EOM) sales file that Boonthavorn (BT) sends itself (folder SO_MDT_EOM/BT, sheet sale_by_branch_detail). It is the figure 'as reported by the chain', used to compare against what the daily feed collected. The branch name (Thai) is used as the branch code, like the BT daily feed.

Read by: [curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md).

# Grain and key

One row per `month_date` (first day of the period), `branch_code` (Thai branch name), `product_code` (ARTICLE_ID, cleaned with `cleanCode`: trimmed). Sales channels (Showroom / Anyhome / Website) are summed into one row; `store_code` is constant 'BT'. Declared `uniqueKey` is month_date, branch_code, product_code.

# Schema

| Column | Type | Description |
|---|---|---|
| `month_date` | DATE | First day of the sales period (DATE_TRUNC to month of START_DATE). |
| `store_code` | STRING | Chain code, constant 'BT' (Boonthavorn). |
| `branch_code` | STRING | Branch identifier: the Thai branch name from the BRANCH column (same convention as the BT daily feed). |
| `product_code` | STRING | Article id (ARTICLE_ID, cleaned code); BT does not send barcodes. |
| `product_name` | STRING | Thai article name (ARTICLE_NAME_TH); one value per key (ANY_VALUE). |
| `sale_qty` | INT64 | Sum of SALE_QTY for the key across sales channels; negative for returns. |
| `sale_amount` | FLOAT64 | Sum of NET_INC_TAX (sales including VAT) for the key; negative for returns. |
| `asatdate` | DATE | MAX of the ASATDATE of the chosen file version; it is the DAG run date, not the period. |

# How it is built

- Definition: `definitions/curated/saleout_mdt/curated_eom_bt.sqlx` (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`).
- `uniqueKey`: `month_date`, `branch_code`, `product_code`.
- Storage options: `{"partitionBy": "month_date", "clusterBy": ["branch_code", "product_code"]}`.
- Reads: [raw_saleout_mdt.eom_bt_sale_by_branch_detail](/initial/raw_saleout_mdt/eom_bt_sale_by_branch_detail.md).
- Full rebuild each run (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`; depends on `curated_schema_saleout` and `create_all_table_raw_saleout_mdt`); partitioned by `month_date`, clustered by branch_code, product_code. Reads the raw external table directly (no validated table). Per `month_date` only the newest file version (latest ASATDATE) that is not made entirely of duplicated rows is used; the run fails if every version of a month is duplicated.

# Examples

Month-end total per branch for one period.

```sql
SELECT month_date, branch_code, SUM(sale_amount) AS sale_amount, SUM(sale_qty) AS sale_qty
FROM `databuffet-nonprd.curated_saleout_mdt.curated_eom_bt`
WHERE month_date = DATE '2026-08-01'
GROUP BY month_date, branch_code
ORDER BY sale_amount DESC
```

---
type: BigQuery Table
title: "mac5_transactions"
description: "One row = one record of source table `mac5_transactions` (ALLKONS_COMMISSION) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_allkons_commission&t=mac5_transactions&page=table"
project_id: databuffet-nonprd
dataset_id: raw_allkons_commission
table_id: mac5_transactions
tags: ["initial", "raw_allkons_commission", "allkons"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx"
    title: "Dataform definition (initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/allkons_commission/mac5_transactions/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mac5_transactions` table from ALLKONS_COMMISSION; nothing is cleaned or deduplicated here.

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inv_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inv_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `receipt_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_method` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `chq_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `chq_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_amt` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bank_account` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_start_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_term` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `company` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_barcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unit` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unit_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_price_amt` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discount_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discount_amt` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_amt` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discount1_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discount1_amt` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_amt1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discount2_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discount2_amt` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_amt2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_dis_amt` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `price_exvat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_note` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `per_dis_cn` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cn_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_dis_cn` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_channel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deleted_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_agent_data` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `root_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `parent_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_area` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_note_item_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `invoice_item_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sort_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_channel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cn_dn_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `calculated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `target_calculated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_allkons_commission` (`definitions/initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/allkons_commission/mac5_transactions/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_allkons_commission.mac5_transactions`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_allkons_commission.mac5_transactions`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

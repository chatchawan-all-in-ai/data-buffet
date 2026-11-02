---
type: BigQuery Table
title: "mac5_transactions"
description: "One row = one sales transaction line used for commission, a record of source table `mac5_transactions` (ALLKONS_COMMISSION) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
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

External table over AVRO files in `gs://file-raw-data/allkons_commission/mac5_transactions/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mac5_transactions` table from ALLKONS_COMMISSION; nothing is cleaned or deduplicated here. Table meaning: MAC5 order, invoice, receipt and credit-note lines with prices, discounts, payments and salesperson data used to calculate sales commission.

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the transaction line. |
| `order_date` | STRING | Sales order date (UTC). |
| `order_no` | STRING | Sales order number. |
| `inv_date` | STRING | Invoice date (UTC). |
| `inv_no` | STRING | Invoice number. |
| `receipt_no` | STRING | Receipt number (e.g. `RI-` + digits). |
| `payment_method` | STRING | Payment method (`Cash`, `Chq`). |
| `chq_no` | STRING | Cheque number. |
| `chq_status` | STRING | Cheque status (`Cleared`, `Due`, `Bounced`). |
| `payment_date` | STRING | Payment date (UTC). |
| `payment_amt` | FLOAT64 | Amount paid on the receipt for this line, in THB. |
| `bank_account` | STRING | Bank account the payment was made to. |
| `credit_start_date` | STRING | Start date of the credit term (UTC). |
| `credit_term` | INT64 | Credit term in days. |
| `company` | STRING | Customer (buyer) name. |
| `sales_id` | STRING | Employee code of the salesperson credited with the sale. |
| `product_barcode` | STRING | Product barcode (EAN-13). |
| `product_name` | STRING | Product name. |
| `unit` | INT64 | Quantity sold (negative for returns). |
| `unit_price` | FLOAT64 | Unit price before discount, in THB. |
| `total_price_amt` | FLOAT64 | Gross line amount before discount (`unit` x `unit_price`), in THB. |
| `discount_type` | STRING | Unit of the first discount (`baht`). |
| `discount_amt` | FLOAT64 | First discount per unit, in THB. |
| `total_amt` | FLOAT64 | Line amount after the first discount, in THB. |
| `discount1_type` | STRING | Unit of the second discount (`baht`). |
| `discount1_amt` | FLOAT64 | Second discount amount, in THB. |
| `total_amt1` | FLOAT64 | Line amount after the second discount, in THB. |
| `discount2_type` | STRING | Unit of the third discount (`baht`). |
| `discount2_amt` | FLOAT64 | Third discount amount, in THB. |
| `total_amt2` | FLOAT64 | Line amount after the third discount, in THB. |
| `total_dis_amt` | FLOAT64 | Total discount as a percentage of the gross line amount. |
| `price_exvat` | FLOAT64 | Net line amount excluding VAT, in THB. |
| `credit_note` | FLOAT64 | Credit note amount applied to the line, in THB (negative). |
| `per_dis_cn` | FLOAT64 | Total discount percentage including the credit note. |
| `cn_no` | STRING | Credit note number. |
| `total_dis_cn` | FLOAT64 | Net line amount after the credit note, in THB. |
| `sales_channel` | STRING | MAC5 sales channel code (`mac5_sales_channels.code`, e.g. `A`, `HP`, `TW`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `deleted_at` | STRING | Timestamp when the record was soft-deleted (NULL while active). |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `sales_agent_data` | STRING | JSON with the salesperson details used for commission (main TA code, sales agent area, employee status, split percentage, product group). |
| `root_id` | STRING | Identifier of the original transaction line that a credit-note adjustment line derives from. |
| `status` | STRING | Commission processing status of the line (`INITIAL`, `ADJUSTED_WITH_CN_RETURN_PRODUCT`, `ADJUSTED_WITH_CN_OR_DN_INVALID_PRICE`). |
| `parent_id` | STRING | Identifier of the parent transaction line (not populated in current data). |
| `sales_area` | STRING | MAC5 sales area code (`mac5_sales_areas.code`, e.g. `A_BK1`). |
| `credit_note_item_id` | STRING | Credit note line key (credit note number and line number). |
| `invoice_item_id` | STRING | Invoice line key (`<inv_no>`, pipe, 4-digit line number). |
| `sort_id` | STRING | Sort key built from the invoice line and receipt numbers (`-no-inv` suffix when not yet invoiced). |
| `delivery_date` | STRING | Delivery date (UTC). |
| `order_channel` | STRING | Channel the order came from (`Offline`, `Online-AllkonsM`). |
| `cn_dn_date` | STRING | Credit or debit note date (UTC). |
| `calculated_at` | STRING | Timestamp when commission was calculated for the line. |
| `target_calculated_at` | STRING | Timestamp when sales-target achievement was calculated for the line. |
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

---
type: BigQuery Table
title: "crm_sale_order_deposit"
description: "One row = one deposit installment of a sale order, a record of source table `crm_sale_order_deposit` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_sale_order_deposit&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_sale_order_deposit
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order_deposit/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order_deposit` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Deposit installments of DERP sale orders with due dates, amounts, payment status and deposit tax invoices. Used by: [validated_derp.crm_sale_order_deposit](/validated/validated_derp/crm_sale_order_deposit.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_deposit_id` | STRING | Unique identifier of the deposit installment. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `installment_seq` | INT64 | Deposit installment number, starting at 1. |
| `payment_method_id` | STRING | Identifier of the payment method. |
| `payment_method_code` | STRING | Payment method code (e.g. `BANK_TRANSFER`, `CASH`, `CHEQUE`, `CREDIT_LIMIT`, `BILL_PAYMENT`, `OTHER_FINANCE`). |
| `payment_term_id` | STRING | Identifier of the payment term. |
| `payment_term_code` | STRING | Payment term code (`N000`/`N030`/`N060` = pay 0/30/60 days after delivery, `N888` = no term). |
| `payment_condition_id` | STRING | Identifier of the payment condition. |
| `payment_condition_code` | STRING | Payment condition code (e.g. `BP_CRM` = by billing cycle, `BFF_LMS` = before delivery, `NOW_LMS` = on delivery, `AFT_LMS` = after delivery, `OTHER`). |
| `amount` | FLOAT64 | Amount due for the deposit installment (THB). |
| `percent` | FLOAT64 | Share of the order amount due for the installment, in percent. |
| `detail` | STRING | Free-text description of the installment. |
| `due_date` | STRING | Due date of the installment. |
| `order_sort` | INT64 | Display order of the installment within its sale order, starting at 0. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `paid_amount` | FLOAT64 | Amount paid for the installment so far (THB). |
| `remaining_amount` | FLOAT64 | Amount of the installment still unpaid (THB). |
| `paid_status` | STRING | Payment status of the installment (`UNPAID`, `PARTIAL`, `PAID`). |
| `paid_date` | STRING | Date and time the installment was paid. |
| `deposit_tax_invoice_no` | STRING | Number of the deposit tax invoice issued for the installment. |
| `deposit_tax_invoice_id` | STRING | Identifier of the deposit tax invoice issued for the installment. |
| `invoiced_amount` | FLOAT64 | Amount of the installment covered by a deposit tax invoice (THB). |
| `deducted_amount` | FLOAT64 | Deposit amount already deducted against invoices (THB). |
| `payment_type` | STRING | Payment type of the installment (`CASH`, `CREDIT` or `OTHER`). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_sale_order_deposit/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_sale_order_deposit`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_sale_order_deposit`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "crm_sale_order_payment_receipt"
description: "One row = one payment received for a sale order, a record of source table `crm_sale_order_payment_receipt` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_sale_order_payment_receipt&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_sale_order_payment_receipt
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order_payment_receipt/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order_payment_receipt` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Payments received against DERP sale orders (deposits or full payments), including voided receipts.

Read by: [validated_derp.crm_sale_order_payment_receipt](/validated/validated_derp/crm_sale_order_payment_receipt.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_payment_receipt_id` | STRING | Unique identifier of the payment receipt. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `source` | STRING | Source of the payment (`MANUAL`, `BANK_KBANK`, `CUSTOMER_CREDIT`, `ALLKONM`). |
| `purpose` | STRING | Purpose of the payment (`DEPOSIT` or `FULL`). |
| `attachment_id` | STRING | Identifier of the attached payment evidence. |
| `bank_txn_ref` | STRING | Bank transaction reference of the payment. |
| `amount` | FLOAT64 | Amount received (THB). |
| `paid_date` | STRING | Date and time the payment was received. |
| `note` | STRING | Free-text note on the payment. |
| `status` | STRING | Status of the receipt (`ACTIVE` or `VOID`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `void_reason` | STRING | Reason the receipt was voided. |
| `voided_at` | STRING | Timestamp when the receipt was voided. |
| `voided_by` | STRING | Identifier of the user who voided the receipt. |
| `voided_by_name` | STRING | Display name of the user who voided the receipt. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_sale_order_payment_receipt/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_sale_order_payment_receipt`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_sale_order_payment_receipt`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

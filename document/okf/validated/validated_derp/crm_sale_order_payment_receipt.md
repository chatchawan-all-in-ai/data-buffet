---
type: BigQuery Table
title: "crm_sale_order_payment_receipt"
description: "One row = one payment received for a sale order from source table `crm_sale_order_payment_receipt`, unique on (sale_order_payment_receipt_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_payment_receipt&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_payment_receipt
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_payment_receipt.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_payment_receipt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_sale_order_payment_receipt`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Payments received against DERP sale orders (deposits or full payments), including voided receipts.
No other repo object reads it.

# Grain and key

One row per `sale_order_payment_receipt_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `paid_date` | DATETIME | Date and time the payment was received. |
| `note` | STRING | Free-text note on the payment. |
| `status` | STRING | Status of the receipt (`ACTIVE` or `VOID`). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `void_reason` | STRING | Reason the receipt was voided. |
| `voided_at` | DATETIME | Timestamp when the receipt was voided. |
| `voided_by` | STRING | Identifier of the user who voided the receipt. |
| `voided_by_name` | STRING | Display name of the user who voided the receipt. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_payment_receipt.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_payment_receipt](/initial/raw_derp/crm_sale_order_payment_receipt.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_payment_receipt_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_payment_receipt`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_payment_receipt_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_payment_receipt`
GROUP BY sale_order_payment_receipt_id
HAVING n > 1
```

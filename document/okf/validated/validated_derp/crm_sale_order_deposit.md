---
type: BigQuery Table
title: "crm_sale_order_deposit"
description: "One row = one deposit installment of a sale order from source table `crm_sale_order_deposit`, unique on (sale_order_deposit_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_deposit&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_deposit
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_deposit.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_deposit.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_sale_order_deposit`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Deposit installments of DERP sale orders with due dates, amounts, payment status and deposit tax invoices.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_deposit_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `due_date` | DATE | Due date of the installment. |
| `order_sort` | INT64 | Display order of the installment within its sale order, starting at 0. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `paid_amount` | FLOAT64 | Amount paid for the installment so far (THB). |
| `remaining_amount` | FLOAT64 | Amount of the installment still unpaid (THB). |
| `paid_status` | STRING | Payment status of the installment (`UNPAID`, `PARTIAL`, `PAID`). |
| `paid_date` | DATETIME | Date and time the installment was paid. |
| `deposit_tax_invoice_no` | STRING | Number of the deposit tax invoice issued for the installment. |
| `deposit_tax_invoice_id` | STRING | Identifier of the deposit tax invoice issued for the installment. |
| `invoiced_amount` | FLOAT64 | Amount of the installment covered by a deposit tax invoice (THB). |
| `deducted_amount` | FLOAT64 | Deposit amount already deducted against invoices (THB). |
| `payment_type` | STRING | Payment type of the installment (`CASH`, `CREDIT` or `OTHER`). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_deposit.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_deposit](/initial/raw_derp/crm_sale_order_deposit.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_deposit_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 329 rows, 141.0 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_deposit`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_deposit_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_deposit`
GROUP BY sale_order_deposit_id
HAVING n > 1
```

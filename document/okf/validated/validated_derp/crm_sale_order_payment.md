---
type: BigQuery Table
title: "crm_sale_order_payment"
description: "One row = one payment plan of a sale order from source table `crm_sale_order_payment`, unique on (sale_order_payment_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_payment&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_payment
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_payment.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_payment.sqlx)"
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

Validated copy of DERP `crm_sale_order_payment`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Payment plans of DERP sale orders: payment method, term, condition and amount.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_payment_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_payment_id` | STRING | Unique identifier of the sale order payment plan. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `payment_seq` | INT64 | Sequence number of the payment plan within the sale order. |
| `payment_method_id` | STRING | Identifier of the payment method. |
| `payment_method_code` | STRING | Payment method code (e.g. `BANK_TRANSFER`, `CASH`, `CHEQUE`, `CREDIT_LIMIT`, `BILL_PAYMENT`, `OTHER_FINANCE`). |
| `payment_method_name` | STRING | Payment method name in Thai. |
| `payment_term_id` | STRING | Identifier of the payment term. |
| `payment_term_code` | STRING | Payment term code (`N000`/`N030`/`N060` = pay 0/30/60 days after delivery, `N888` = no term). |
| `payment_term_name` | STRING | Payment term description in Thai (e.g. pay 60 days after delivery). |
| `payment_term_other` | STRING | Free-text payment term entered when no standard term applies. |
| `payment_condition_id` | STRING | Identifier of the payment condition. |
| `payment_condition_code` | STRING | Payment condition code (e.g. `BP_CRM` = by billing cycle, `BFF_LMS` = before delivery, `NOW_LMS` = on delivery, `AFT_LMS` = after delivery, `OTHER`). |
| `payment_condition_name` | STRING | Payment condition description in Thai. |
| `payment_condition_other` | STRING | Free-text payment condition entered when no standard condition applies. |
| `amount` | FLOAT64 | Amount covered by the payment plan (THB). |
| `percent` | FLOAT64 | Share of the order amount covered by the payment plan, in percent. |
| `detail` | STRING | Free-text description of the payment plan. |
| `order_sort` | INT64 | Display order of the row within its sale order, starting at 0. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_payment.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_payment](/initial/raw_derp/crm_sale_order_payment.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_payment_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,094 rows, 1.7 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_payment`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_payment_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_payment`
GROUP BY sale_order_payment_id
HAVING n > 1
```

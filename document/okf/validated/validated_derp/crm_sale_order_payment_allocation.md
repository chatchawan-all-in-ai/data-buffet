---
type: BigQuery Table
title: "crm_sale_order_payment_allocation"
description: "One row = one allocation of a payment receipt to a deposit installment from source table `crm_sale_order_payment_allocation`, unique on (sale_order_payment_allocation_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_payment_allocation&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_payment_allocation
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_payment_allocation.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_payment_allocation.sqlx)"
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

Validated copy of DERP `crm_sale_order_payment_allocation`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Allocations of received payments to the deposit installments of DERP sale orders.
No other repo object reads it.

# Grain and key

One row per `sale_order_payment_allocation_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_payment_allocation_id` | STRING | Unique identifier of the payment allocation. |
| `receipt_id` | STRING | Identifier of the payment receipt being allocated (`crm_sale_order_payment_receipt`). |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `installment_seq` | INT64 | Deposit installment number the amount is allocated to. |
| `sale_order_deposit_id` | STRING | Identifier of the deposit installment (`crm_sale_order_deposit.sale_order_deposit_id`). |
| `amount` | FLOAT64 | Amount of the receipt allocated to the deposit installment (THB). |
| `note` | STRING | Free-text note. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_payment_allocation.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_payment_allocation](/initial/raw_derp/crm_sale_order_payment_allocation.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY created_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_payment_allocation_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_payment_allocation`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_payment_allocation_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_payment_allocation`
GROUP BY sale_order_payment_allocation_id
HAVING n > 1
```

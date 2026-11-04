---
type: BigQuery Table
title: "crm_sale_order_approval_log"
description: "One row = one approval action on a sale order from source table `crm_sale_order_approval_log`, unique on (sale_order_approval_log_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_approval_log&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_approval_log
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_approval_log.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_approval_log.sqlx)"
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

Validated copy of DERP `crm_sale_order_approval_log`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Log of approval actions (approve, reject, credit and pay-in approvals) on DERP sale orders with the status change.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_approval_log_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_approval_log_id` | STRING | Unique identifier of the approval log entry. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `rev_no` | INT64 | Sale order revision number this record belongs to. |
| `action_type` | STRING | Approval action taken (e.g. `APPROVE`, `REJECT`, `CREDIT_APPROVE`, `PAYIN_APPROVE_CASH`, `PAYIN_APPROVE_DEPOSIT`, `PAYIN_RETURN`). |
| `prev_status` | STRING | Sale order status code before the action (same codes as `crm_sale_order.status`). |
| `next_status` | STRING | Sale order status code after the action (same codes as `crm_sale_order.status`). |
| `payment_type` | STRING | Payment type of the order at the time of the action (`CASH`, `CREDIT` or `OTHER`). |
| `reject_reason_code` | STRING | Rejection reason code (e.g. `01`). |
| `reject_reason_name` | STRING | Rejection reason description in Thai. |
| `note` | STRING | Free-text note from the approver. |
| `context_data` | STRING | JSON with extra context of the action (e.g. attached files, revision number, creation source). |
| `notified_at` | DATETIME | Timestamp when the notification about the action was sent. |
| `notified_via` | STRING | Channel the notification was sent through (e.g. `IN_SYSTEM`). |
| `action_by` | STRING | Identifier of the user who performed the action. |
| `action_by_name` | STRING | Display name of the user who performed the action. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_approval_log.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_approval_log](/initial/raw_derp/crm_sale_order_approval_log.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY created_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_approval_log_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_approval_log`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_approval_log_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_approval_log`
GROUP BY sale_order_approval_log_id
HAVING n > 1
```

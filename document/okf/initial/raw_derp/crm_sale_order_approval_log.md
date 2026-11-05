---
type: BigQuery Table
title: "crm_sale_order_approval_log"
description: "One row = one approval action on a sale order, a record of source table `crm_sale_order_approval_log` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_sale_order_approval_log&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_sale_order_approval_log
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order_approval_log/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order_approval_log` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Log of approval actions (approve, reject, credit and pay-in approvals) on DERP sale orders with the status change.

Read by: [validated_derp.crm_sale_order_approval_log](/validated/validated_derp/crm_sale_order_approval_log.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

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
| `notified_at` | STRING | Timestamp when the notification about the action was sent. |
| `notified_via` | STRING | Channel the notification was sent through (e.g. `IN_SYSTEM`). |
| `action_by` | STRING | Identifier of the user who performed the action. |
| `action_by_name` | STRING | Display name of the user who performed the action. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_sale_order_approval_log/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_sale_order_approval_log`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_sale_order_approval_log`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

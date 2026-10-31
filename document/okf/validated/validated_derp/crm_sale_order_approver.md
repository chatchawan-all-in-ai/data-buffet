---
type: BigQuery Table
title: "crm_sale_order_approver"
description: "One row = one cleaned copy of the source table `crm_sale_order_approver`, unique on (sale_order_approver_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_approver&page=table"
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_approver.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_approver.sqlx)"
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

Validated copy of DERP `crm_sale_order_approver`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_approver_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_approver_id` | STRING | Meaning not documented in the repo. |
| `sale_order_id` | STRING | Meaning not documented in the repo. |
| `rev_no` | INT64 | Meaning not documented in the repo. |
| `employee_id` | STRING | Meaning not documented in the repo. |
| `user_id` | STRING | Meaning not documented in the repo. |
| `employee_no` | STRING | Meaning not documented in the repo. |
| `approver_name` | STRING | Meaning not documented in the repo. |
| `alternate_level` | INT64 | Meaning not documented in the repo. |
| `approver_role` | STRING | Meaning not documented in the repo. |
| `is_primary` | BOOL | Meaning not documented in the repo. |
| `approval_scope_id` | STRING | Meaning not documented in the repo. |
| `approval_scope_code` | STRING | Meaning not documented in the repo. |
| `approval_scope_name` | STRING | Meaning not documented in the repo. |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_approver.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_approver](/initial/raw_derp/crm_sale_order_approver.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY created_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_approver_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 983 rows, 369.5 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_approver`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_approver_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_approver`
GROUP BY sale_order_approver_id
HAVING n > 1
```

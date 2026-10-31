---
type: BigQuery Table
title: "crm_customer_segment"
description: "One row = one cleaned copy of the source table `crm_customer_segment`, unique on (customer_segment_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_segment&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_segment
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_segment.sqlx"
    title: "Dataform definition (validated/derp/crm_customer_segment.sqlx)"
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

Validated copy of DERP `crm_customer_segment`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `customer_segment_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_segment_id` | STRING | Meaning not documented in the repo. |
| `customer_master_id` | STRING | Meaning not documented in the repo. |
| `customer_code` | STRING | Meaning not documented in the repo. |
| `customer_group_id` | STRING | Meaning not documented in the repo. |
| `item_customer_group` | STRING | Meaning not documented in the repo. |
| `customer_type` | STRING | Meaning not documented in the repo. |
| `business_type` | STRING | Meaning not documented in the repo. |
| `company_chain` | STRING | Meaning not documented in the repo. |
| `region` | STRING | Meaning not documented in the repo. |
| `customer_category_level` | INT64 | Meaning not documented in the repo. |
| `customer_category_path` | STRING | Meaning not documented in the repo. |
| `marketing_group_level` | INT64 | Meaning not documented in the repo. |
| `marketing_group_path` | STRING | Meaning not documented in the repo. |
| `sales_group_level` | INT64 | Meaning not documented in the repo. |
| `sales_group_path` | STRING | Meaning not documented in the repo. |
| `accounting_group_level` | INT64 | Meaning not documented in the repo. |
| `accounting_group_path` | STRING | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `updated_by_name` | STRING | Meaning not documented in the repo. |
| `is_sync` | BOOL | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_segment.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_segment](/initial/raw_derp/crm_customer_segment.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_segment_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 22,518 rows, 2.7 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_segment`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT customer_segment_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_customer_segment`
GROUP BY customer_segment_id
HAVING n > 1
```

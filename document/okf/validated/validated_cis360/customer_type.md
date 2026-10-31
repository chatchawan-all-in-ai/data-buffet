---
type: BigQuery Table
title: "customer_type"
description: "One row = one cleaned copy of the source table `customer_type`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_cis360&t=customer_type&page=table"
project_id: databuffet-nonprd
dataset_id: validated_cis360
table_id: customer_type
tags: ["validated", "validated_cis360", "cis360", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/cis360/customer_type.sqlx"
    title: "Dataform definition (validated/cis360/customer_type.sqlx)"
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

Validated copy of CIS360 `customer_type`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [dimension_table.dim_customer](/dimension/dim_customer.md).

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Surrogate identifier from the source system (the primary key). |
| `customer_type_name` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `customer_type_name_en` | STRING | Meaning not documented in the repo. |
| `customer_type_code` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `customer_type_order` | INT64 | Meaning not documented in the repo. |
| `is_constant` | BOOL | Meaning not documented in the repo. |
| `active_status` | BOOL | Meaning not documented in the repo. |
| `is_delete` | BOOL | Meaning not documented in the repo. |
| `create_date` | DATETIME | Meaning not documented in the repo. |
| `create_by` | STRING | Meaning not documented in the repo. |
| `create_by_platform` | STRING | Meaning not documented in the repo. |
| `update_by_platform` | STRING | Meaning not documented in the repo. |
| `update_date` | DATETIME | Meaning not documented in the repo. |
| `update_by` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/cis360/customer_type.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_cis360.customer_type](/initial/raw_cis360/customer_type.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 2 rows, 206 B.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_cis360.customer_type`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_cis360.customer_type`
GROUP BY id
HAVING n > 1
```

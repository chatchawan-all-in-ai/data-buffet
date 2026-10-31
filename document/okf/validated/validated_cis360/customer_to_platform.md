---
type: BigQuery Table
title: "customer_to_platform"
description: "One row = one cleaned copy of the source table `customer_to_platform`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_cis360&t=customer_to_platform&page=table"
project_id: databuffet-nonprd
dataset_id: validated_cis360
table_id: customer_to_platform
tags: ["validated", "validated_cis360", "cis360", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/cis360/customer_to_platform.sqlx"
    title: "Dataform definition (validated/cis360/customer_to_platform.sqlx)"
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

Validated copy of CIS360 `customer_to_platform`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Surrogate identifier from the source system (the primary key). |
| `customer_profile_id` | STRING | Meaning not documented in the repo. |
| `platform_id` | INT64 | Meaning not documented in the repo. |
| `create_relationship_date` | DATETIME | Meaning not documented in the repo. |
| `is_delete` | BOOL | Meaning not documented in the repo. |
| `create_date` | DATETIME | Meaning not documented in the repo. |
| `create_by` | STRING | Meaning not documented in the repo. |
| `create_by_platform` | STRING | Meaning not documented in the repo. |
| `update_by_platform` | STRING | Meaning not documented in the repo. |
| `update_date` | DATETIME | Meaning not documented in the repo. |
| `update_by` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/cis360/customer_to_platform.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_cis360.customer_to_platform](/initial/raw_cis360/customer_to_platform.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 68,510 rows, 9.9 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_cis360.customer_to_platform`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_cis360.customer_to_platform`
GROUP BY id
HAVING n > 1
```

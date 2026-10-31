---
type: BigQuery Table
title: "crm_customer_data_zone"
description: "One row = one cleaned copy of the source table `crm_customer_data_zone`, unique on (customer_data_zone_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_data_zone&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_data_zone
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_data_zone.sqlx"
    title: "Dataform definition (validated/derp/crm_customer_data_zone.sqlx)"
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

Validated copy of DERP `crm_customer_data_zone`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `customer_data_zone_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_data_zone_id` | STRING | Meaning not documented in the repo. |
| `customer_master_id` | STRING | Meaning not documented in the repo. |
| `customer_code` | STRING | Meaning not documented in the repo. |
| `data_zone_id` | STRING | Meaning not documented in the repo. |
| `level1_id` | STRING | Meaning not documented in the repo. |
| `level1_code` | STRING | Meaning not documented in the repo. |
| `level1_name` | STRING | Meaning not documented in the repo. |
| `level2_id` | STRING | Meaning not documented in the repo. |
| `level2_code` | STRING | Meaning not documented in the repo. |
| `level2_name` | STRING | Meaning not documented in the repo. |
| `level3_id` | STRING | Meaning not documented in the repo. |
| `level3_code` | STRING | Meaning not documented in the repo. |
| `level3_name` | STRING | Meaning not documented in the repo. |
| `path_id` | STRING | Meaning not documented in the repo. |
| `path_code` | STRING | Meaning not documented in the repo. |
| `path_name` | STRING | Meaning not documented in the repo. |
| `zone_type` | STRING | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `valid_from` | STRING | Meaning not documented in the repo. |
| `valid_to` | STRING | Meaning not documented in the repo. |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `updated_by_name` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_data_zone.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_data_zone](/initial/raw_derp/crm_customer_data_zone.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY COALESCE(updated_at, created_at) DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_data_zone_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 8 rows, 5.6 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_data_zone`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT customer_data_zone_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_customer_data_zone`
GROUP BY customer_data_zone_id
HAVING n > 1
```

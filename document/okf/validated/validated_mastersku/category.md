---
type: BigQuery Table
title: "category"
description: "One row = one cleaned copy of the source table `category`, unique on (cat_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=category&page=table"
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/category.sqlx"
    title: "Dataform definition (validated/mastersku/category.sqlx)"
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

Validated copy of MASTERSKU `category`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md).

# Grain and key

One row per `cat_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `cat_id` | STRING | Meaning not documented in the repo. |
| `cat_code` | STRING | Meaning not documented in the repo. |
| `cat_name` | STRING | Meaning not documented in the repo. |
| `cat_d365_code` | STRING | Meaning not documented in the repo. |
| `cat_description` | STRING | Meaning not documented in the repo. |
| `cat_tag` | STRING | Meaning not documented in the repo. |
| `cat_parent_id` | STRING | Meaning not documented in the repo. |
| `cat_level` | INT64 | Meaning not documented in the repo. |
| `cat_img_name` | STRING | Meaning not documented in the repo. |
| `cat_img_path` | STRING | Meaning not documented in the repo. |
| `cat_vendor_id` | STRING | Meaning not documented in the repo. |
| `cat_is_active` | BOOL | Meaning not documented in the repo. |
| `cat_is_use` | BOOL | Meaning not documented in the repo. |
| `cat_created_date` | DATETIME | Meaning not documented in the repo. |
| `cat_created_by` | STRING | Meaning not documented in the repo. |
| `cat_updated_date` | DATETIME | Meaning not documented in the repo. |
| `cat_updated_by` | STRING | Meaning not documented in the repo. |
| `cat_specific_field` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/category.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.category](/initial/raw_mastersku/category.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `cat_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,242 rows, 559.4 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.category`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT cat_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.category`
GROUP BY cat_id
HAVING n > 1
```

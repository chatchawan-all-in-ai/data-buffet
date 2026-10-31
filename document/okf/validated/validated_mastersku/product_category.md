---
type: BigQuery Table
title: "product_category"
description: "One row = one cleaned copy of the source table `product_category`, unique on (pc_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product_category&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: product_category
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product_category.sqlx"
    title: "Dataform definition (validated/mastersku/product_category.sqlx)"
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

Validated copy of MASTERSKU `product_category`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `pc_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `pc_id` | STRING | Meaning not documented in the repo. |
| `pc_prod_id` | STRING | Meaning not documented in the repo. |
| `pc_cat_id` | STRING | Meaning not documented in the repo. |
| `pc_is_ise` | BOOL | Meaning not documented in the repo. |
| `pc_is_active` | BOOL | Meaning not documented in the repo. |
| `pc_created_date` | DATETIME | Meaning not documented in the repo. |
| `pc_updated_date` | DATETIME | Meaning not documented in the repo. |
| `pc_created_by` | STRING | Meaning not documented in the repo. |
| `pc_updated_by` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product_category.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product_category](/initial/raw_mastersku/product_category.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `pc_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 107 rows, 22.6 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product_category`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT pc_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product_category`
GROUP BY pc_id
HAVING n > 1
```

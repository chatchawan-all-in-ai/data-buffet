---
type: BigQuery Table
title: "category"
description: "One row = one product category from source table `category`, unique on (cat_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=category&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: category
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MASTERSKU `category`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product category tree (up to 5 levels) of the old product master MASTERSKU.

Read by: [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md).

# Grain and key

One row per `cat_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `cat_id` | STRING | Unique identifier (UUID) of the category. |
| `cat_code` | STRING | Category code (hierarchical digits, e.g. `0301030204`). |
| `cat_name` | STRING | Category name. |
| `cat_d365_code` | STRING | Category code in Dynamics 365. |
| `cat_description` | STRING | Category description. |
| `cat_tag` | STRING | Search tags of the category as JSON (`{"cat_tag":[...]}`). |
| `cat_parent_id` | STRING | Parent category (FK to `category.cat_id`; NULL at level 1). |
| `cat_level` | INT64 | Level of the category in the hierarchy (1 = top, up to 5). |
| `cat_img_name` | STRING | File name of the category image. |
| `cat_img_path` | STRING | Storage path of the category image. |
| `cat_vendor_id` | STRING | Vendor that owns the category (FK to `vendor.vd_id`). |
| `cat_is_active` | BOOL | Active flag of the record. |
| `cat_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `cat_created_date` | DATETIME | Timestamp when the record was created. |
| `cat_created_by` | STRING | Identifier of the user who created the record. |
| `cat_updated_date` | DATETIME | Timestamp when the record was last updated. |
| `cat_updated_by` | STRING | Identifier of the user who last updated the record. |
| `cat_specific_field` | STRING | Category-specific attribute labels as JSON (`{"specific":[...]}`). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/category.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.category](/initial/raw_mastersku/category.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `cat_id`.

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

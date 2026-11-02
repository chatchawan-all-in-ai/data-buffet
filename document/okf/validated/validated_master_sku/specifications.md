---
type: BigQuery Table
title: "specifications"
description: "One row = one attribute assigned to one specification group from source table `specifications`, unique on (group_id, attribute_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=specifications&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: specifications
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/specifications.sqlx"
    title: "Dataform definition (validated/master_sku/specifications.sqlx)"
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

Validated copy of MASTER_SKU `specifications`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Attributes assigned to each master_sku specification group, with display order and required/variant flags.
No other table or view in this repository reads it.

# Grain and key

One row per `group_id`, `attribute_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `group_id` | STRING | Specification group (FK to `spec_groups.id`). |
| `attribute_id` | STRING | Specification attribute (FK to `spec_attributes.id`). |
| `sort_order` | INT64 | Display order of the attribute within the group. |
| `is_displayed` | BOOL | Flag marking the attribute as shown on the product. |
| `is_required` | BOOL | Flag marking the attribute as mandatory for products in the group. |
| `is_variant` | BOOL | Flag marking the attribute as a variant dimension that distinguishes SKUs in the group. |
| `status` | STRING | Record status (`Active`, `Inactive`, `Deleted`). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/master_sku/specifications.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.specifications](/initial/raw_master_sku/specifications.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `group_id`, `attribute_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 59,490 rows, 6.8 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.specifications`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT group_id, attribute_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.specifications`
GROUP BY group_id, attribute_id
HAVING n > 1
```

---
type: BigQuery Table
title: "common_codes"
description: "One row = one code value in one code list from source table `common_codes`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=common_codes&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: common_codes
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/common_codes.sqlx"
    title: "Dataform definition (validated/master_sku/common_codes.sqlx)"
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

Validated copy of MASTER_SKU `common_codes`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Shared code lists of master_sku 3.0 (units of measure, barcode formats, languages, statuses, product types, synonym types, color descriptors and group types).
Used by: [curated_master_sku.curated_products](/curated/curated_master_sku/curated_products.md), [curated_master_sku.product_for_aisearch_v3](/curated/curated_master_sku/product_for_aisearch_v3.md).

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the code. |
| `type` | STRING | Code list the value belongs to (e.g. `sales-unit`, `uom-length`, `uom-weight`, `barcode-format`, `language`, `synonym-type`, `color-descriptor`, `product-type`). |
| `code` | STRING | Code value within its list (e.g. `KG`, `EAN13`, `th`). |
| `name` | STRING | Display name of the code. |
| `description` | STRING | Description of the code. |
| `sort_order` | INT64 | Display order within the code list. |
| `is_system` | BOOL | Flag marking a system-defined code. |
| `status` | STRING | Record status (`Active`, `Inactive`, `Deleted`). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/master_sku/common_codes.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.common_codes](/initial/raw_master_sku/common_codes.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.common_codes`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.common_codes`
GROUP BY id
HAVING n > 1
```

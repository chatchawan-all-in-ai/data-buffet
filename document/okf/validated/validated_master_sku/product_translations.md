---
type: BigQuery Table
title: "product_translations"
description: "One row = one product text in one language from source table `product_translations`, unique on (product_id, language_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=product_translations&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: product_translations
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/product_translations.sqlx"
    title: "Dataform definition (validated/master_sku/product_translations.sqlx)"
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

Validated copy of MASTER_SKU `product_translations`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Translated (Thai/English) names and descriptive texts of master_sku products.
No other table or view in this repository reads it.

# Grain and key

One row per `product_id`, `language_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `product_id` | STRING | Product being translated (FK to `products.id`). |
| `language_id` | STRING | Language of the translation (FK to `common_codes.id` of type `language`: `en` or `th`). |
| `name` | STRING | Product name in this language. |
| `description_short` | STRING | Short product description in this language. |
| `description` | STRING | Product description in this language. |
| `property` | STRING | Product properties text in this language. |
| `detail` | STRING | Product detail text in this language. |
| `instruction` | STRING | Usage instructions in this language. |
| `recommendation` | STRING | Usage recommendations in this language. |
| `caution` | STRING | Caution/warning text in this language. |
| `installation` | STRING | Installation instructions in this language. |
| `transportation` | STRING | Transportation/handling instructions in this language. |
| `stack_over` | STRING | Stacking limit instructions in this language. |
| `warranty_detail` | STRING | Warranty terms in this language. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/master_sku/product_translations.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.product_translations](/initial/raw_master_sku/product_translations.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `product_id`, `language_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.product_translations`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT product_id, language_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.product_translations`
GROUP BY product_id, language_id
HAVING n > 1
```

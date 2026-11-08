---
type: BigQuery Table
title: "functional_group_translations"
description: "One row per `functional_group_translations` from source table `functional_group_translations`, unique on (functional_group_id, language_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=functional_group_translations&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: functional_group_translations
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/functional_group_translations.sqlx"
    title: "Dataform definition (validated/master_sku/functional_group_translations.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T21:13:49+07:00" }
status: draft
---

# What it is

Validated copy of MASTER_SKU `functional_group_translations`: string values are cleaned, types are cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Localized names and descriptions for product functional groups.

# Grain and key

One row per (functional_group_id, language_id). The composite key is declared in both `uniqueKey` and `pk_key`; the definition adds it as a `NOT ENFORCED` primary key after a full build.

# Schema

| Column | Type | Description |
|---|---|---|
| `functional_group_id` | STRING | Identifier of the related functional group. |
| `language_id` | STRING | Identifier of the language. |
| `name` | STRING | Name of the record. |
| `description` | STRING | Descriptive text for the record. |
| `created_at` | DATETIME | UTC timestamp when the record was created. |
| `updated_at` | DATETIME | UTC timestamp when the record was last updated. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date parsed from the raw ASATDATE partition; used for deduplication and partitioning. |

# How it is built

- Definition: `definitions/validated/master_sku/functional_group_translations.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.functional_group_translations](/initial/raw_master_sku/functional_group_translations.md).
- Incremental runs read raw partitions within the configured `BACKFILL_DAYS` window and MERGE on `uniqueKey`; the first or a full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY functional_group_id, language_id ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `functional_group_id, language_id`.

# Examples

Recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.functional_group_translations`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT functional_group_id, language_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.functional_group_translations`
GROUP BY functional_group_id, language_id
HAVING n > 1
```

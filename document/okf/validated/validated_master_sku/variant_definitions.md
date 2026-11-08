---
type: BigQuery Table
title: "variant_definitions"
description: "One row per `variant_definitions` from source table `variant_definitions`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=variant_definitions&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: variant_definitions
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/variant_definitions.sqlx"
    title: "Dataform definition (validated/master_sku/variant_definitions.sqlx)"
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

Validated copy of MASTER_SKU `variant_definitions`: string values are cleaned, types are cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Definitions for product or media variants.

# Grain and key

One row per (id). The key is declared in both `uniqueKey` and `pk_key`; the definition adds it as a `NOT ENFORCED` primary key after a full build.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source identifier for the record. |
| `reference_type_id` | STRING | Identifier of the reference type. |
| `media_type` | STRING | Media category. |
| `variant_type` | STRING | Variant category. |
| `width` | INT64 | Width in source units. |
| `height` | INT64 | Height in source units. |
| `max_duration_seconds` | FLOAT64 | Maximum media duration in seconds. |
| `bitrate_kbps` | INT64 | Media bitrate in kilobits per second. |
| `format` | STRING | Media format. |
| `extension` | STRING | File extension. |
| `processing_rules` | STRING | Serialized processing rules. |
| `auto_generate` | BOOL | Whether the variant is generated automatically. |
| `status` | STRING | Source status of the record. |
| `created_at` | DATETIME | UTC timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | UTC timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date parsed from the raw ASATDATE partition; used for deduplication and partitioning. |

# How it is built

- Definition: `definitions/validated/master_sku/variant_definitions.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.variant_definitions](/initial/raw_master_sku/variant_definitions.md).
- Incremental runs read raw partitions within the configured `BACKFILL_DAYS` window and MERGE on `uniqueKey`; the first or a full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY id ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.variant_definitions`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.variant_definitions`
GROUP BY id
HAVING n > 1
```

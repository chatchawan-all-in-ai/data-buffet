---
type: BigQuery Table
title: "variant_definitions"
description: "One row = one source record in `variant_definitions` (MASTER_SKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=variant_definitions&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: variant_definitions
tags: ["initial", "raw_master_sku", "master_sku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx"
    title: "Dataform definition (initial/master_sku/create_all_table_raw_master_sku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:codex", at: "2026-11-08T21:13:49+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/master_sku/variant_definitions/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of `variant_definitions` from MASTER_SKU; no columns are cleaned or deduplicated here. Table meaning: Definitions for product or media variants.

Read by: [validated_master_sku.variant_definitions](/validated/validated_master_sku/variant_definitions.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; the validated table defines the key and keeps the newest row.

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
| `created_at` | STRING | UTC timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | UTC timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition date (`YYYYMMDD`) of the GCS extract. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery; queries read the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/variant_definitions/*`.
- Refresh: the extract job writes the files; the external table sees them without a Dataform refresh.

# Examples

Rows in a recent extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.variant_definitions`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-backed row counts per extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_master_sku.variant_definitions`
GROUP BY ASATDATE
ORDER BY ASATDATE
```

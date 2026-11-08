---
type: BigQuery Table
title: "product_assets"
description: "One row = one source record in `product_assets` (MASTER_SKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=product_assets&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: product_assets
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

External table over AVRO files in `gs://file-raw-data/master_sku/product_assets/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of `product_assets` from MASTER_SKU; no columns are cleaned or deduplicated here. Table meaning: Digital assets and files associated with products or other source references.

Read by: [validated_master_sku.product_assets](/validated/validated_master_sku/product_assets.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; the validated table defines the key and keeps the newest row.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source identifier for the record. |
| `parent_id` | STRING | Identifier of the parent record. |
| `reference_type_id` | STRING | Identifier of the reference type. |
| `reference_id` | STRING | Identifier of the referenced source record. |
| `variant_id` | STRING | Identifier of the related variant. |
| `asset_type_id` | STRING | Identifier of the asset type. |
| `language_id` | STRING | Identifier of the language. |
| `file_name` | STRING | Asset file name. |
| `description` | STRING | Descriptive text for the record. |
| `tags` | STRING | Serialized asset tags. |
| `file_path` | STRING | Asset file path in the source system. |
| `file_hash` | STRING | File content hash. |
| `size_bytes` | INT64 | Asset file size in bytes. |
| `mime_type` | STRING | MIME type of the asset. |
| `extension` | STRING | File extension. |
| `width` | INT64 | Width in source units. |
| `height` | INT64 | Height in source units. |
| `duration_seconds` | FLOAT64 | Media duration in seconds. |
| `bitrate_kbps` | INT64 | Media bitrate in kilobits per second. |
| `metadata` | STRING | Additional serialized metadata. |
| `sort_order` | INT64 | Display order within the group. |
| `status` | STRING | Source status of the record. |
| `created_at` | STRING | UTC timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | UTC timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `vendor_id` | STRING | Identifier of the related vendor. |
| `ASATDATE` | STRING | Hive partition date (`YYYYMMDD`) of the GCS extract. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery; queries read the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/product_assets/*`.
- Refresh: the extract job writes the files; the external table sees them without a Dataform refresh.

# Examples

Rows in a recent extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.product_assets`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-backed row counts per extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_master_sku.product_assets`
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "business_unit_translations"
description: "One row = one localized business unit names and descriptions source record from MASTER_SKU, as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=business_unit_translations&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: business_unit_translations
tags: ["initial", "raw_master_sku", "master_sku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx"
    title: "Dataform definition (initial/master_sku/create_all_table_raw_master_sku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki: initial layer"
generated: { by: "agent:codex", at: "2026-11-08T23:59:00+07:00" }
status: draft
---



# What it is

External table over AVRO files in `gs://file-raw-data/master_sku/business_unit_translations/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of `business_unit_translations` from MASTER_SKU; no columns are cleaned or deduplicated here.

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; the validated table defines the key and keeps the newest row.

# Schema

| Column | Type | Description |
|---|---|---|
| `business_unit_id` | STRING | Business unit identifier. |
| `language_id` | STRING | Language identifier. |
| `name` | STRING | Localized business unit name. |
| `description` | STRING | Localized business unit description. |
| `created_at` | STRING | UTC creation timestamp. |
| `created_by` | STRING | Creator identifier. |
| `updated_at` | STRING | UTC update timestamp. |
| `updated_by` | STRING | Updater identifier. |
| `ASATDATE` | STRING | Hive partition date (`YYYYMMDD`) of the GCS extract. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery; queries read the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/business_unit_translations/*`.
- Refresh: the extract job writes the files; the external table sees them without a Dataform refresh.

# Examples

Rows in a recent extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.business_unit_translations`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

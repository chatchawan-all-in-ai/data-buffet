---
type: BigQuery Table
title: "category"
description: "One row = one product category, a record of source table `category` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=category&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mastersku
table_id: category
tags: ["initial", "raw_mastersku", "mastersku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx"
    title: "Dataform definition (initial/mastersku/create_all_table_raw_mastersku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mastersku/category/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `category` table from MASTERSKU; nothing is cleaned or deduplicated here. Table meaning: Product category tree (up to 5 levels) of the old product master MASTERSKU.

Read by: [validated_mastersku.category](/validated/validated_mastersku/category.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

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
| `cat_created_date` | STRING | Timestamp when the record was created. |
| `cat_created_by` | STRING | Identifier of the user who created the record. |
| `cat_updated_date` | STRING | Timestamp when the record was last updated. |
| `cat_updated_by` | STRING | Identifier of the user who last updated the record. |
| `cat_specific_field` | STRING | Category-specific attribute labels as JSON (`{"specific":[...]}`). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mastersku` (`definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mastersku/category/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mastersku.category`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mastersku.category`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

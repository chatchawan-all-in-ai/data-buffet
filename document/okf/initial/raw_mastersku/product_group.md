---
type: BigQuery Table
title: "product_group"
description: "One row = one record of source table `product_group` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=product_group&page=table"
tags: ["initial", "raw_mastersku", "mastersku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx"
    title: "Dataform definition (initial/mastersku/create_all_table_raw_mastersku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mastersku/product_group/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `product_group` table from MASTERSKU; nothing is cleaned or deduplicated here. Used by: [validated_mastersku.product_group](/validated/validated_mastersku/product_group.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `pg_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_description` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension_d365_1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension_d365_2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension_d365_3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_dimension_d365_4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_vendor_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_is_system` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_is_active` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_is_use` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_created_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_updated_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_brand_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_sku` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_barcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_er_source` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_tag` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_file_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pg_cg_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mastersku` (`definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mastersku/product_group/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mastersku.product_group`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mastersku.product_group`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

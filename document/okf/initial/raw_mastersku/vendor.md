---
type: BigQuery Table
title: "vendor"
description: "One row = one record of source table `vendor` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=vendor&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mastersku
table_id: vendor
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

External table over AVRO files in `gs://file-raw-data/mastersku/vendor/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `vendor` table from MASTERSKU; nothing is cleaned or deduplicated here. Used by: [validated_mastersku.vendor](/validated/validated_mastersku/vendor.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `vd_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_api_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_coporate_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_country_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_province_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_district_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_sub_district_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_zipcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_email` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_address` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_organize_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_business_type_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_document_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_document_path` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_is_dbd` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_account_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_kyc_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_is_active` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_is_use` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_created_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vd_updated_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mastersku` (`definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mastersku/vendor/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mastersku.vendor`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mastersku.vendor`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

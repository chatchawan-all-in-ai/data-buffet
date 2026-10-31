---
type: BigQuery Table
title: "vendors"
description: "One row = one record of source table `vendors` (MASTER_SKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=vendors&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: vendors
tags: ["initial", "raw_master_sku", "master_sku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx"
    title: "Dataform definition (initial/master_sku/create_all_table_raw_master_sku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/master_sku/vendors/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `vendors` table from MASTER_SKU; nothing is cleaned or deduplicated here. Used by: [validated_master_sku.vendors](/validated/validated_master_sku/vendors.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `allkons_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `auth_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `legal_entity_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `phone_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `country_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `province_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `district_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sub_district_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `postal_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `email` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `address` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `company_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `business_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `document_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_dbd` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `account_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `kyc_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/vendors/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.vendors`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_master_sku.vendors`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

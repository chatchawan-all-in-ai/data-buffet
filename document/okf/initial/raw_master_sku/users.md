---
type: BigQuery Table
title: "users"
description: "One row = one source record in `users` (MASTER_SKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=users&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: users
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

External table over AVRO files in `gs://file-raw-data/master_sku/users/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of `users` from MASTER_SKU; no columns are cleaned or deduplicated here. Table meaning: User accounts registered in the master_sku source.

Read by: [validated_master_sku.users](/validated/validated_master_sku/users.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; the validated table defines the key and keeps the newest row.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source identifier for the record. |
| `first_name` | STRING | User first name. |
| `last_name` | STRING | User last name. |
| `phone_no` | STRING | Telephone number. |
| `email` | STRING | Email address. |
| `approve_status` | STRING | User approval status. |
| `failed_attempts` | INT64 | Number of failed authentication attempts. |
| `is_locked` | BOOL | Whether the user account is locked. |
| `auth_center_id` | STRING | Identifier of the external authentication center. |
| `status` | STRING | Source status of the record. |
| `created_at` | STRING | UTC timestamp when the record was created. |
| `updated_at` | STRING | UTC timestamp when the record was last updated. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition date (`YYYYMMDD`) of the GCS extract. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery; queries read the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/users/*`.
- Refresh: the extract job writes the files; the external table sees them without a Dataform refresh.

# Examples

Rows in a recent extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.users`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-backed row counts per extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_master_sku.users`
GROUP BY ASATDATE
ORDER BY ASATDATE
```

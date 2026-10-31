---
type: BigQuery Table
title: "crm_sale_order_delivery"
description: "One row = one record of source table `crm_sale_order_delivery` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_sale_order_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_sale_order_delivery
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order_delivery/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order_delivery` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.crm_sale_order_delivery](/validated/validated_derp/crm_sale_order_delivery.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_delivery_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_order_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `round_no` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_address_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_address_text` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `receiver_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `receiver_phone` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark_logistic` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_sort` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `time_start` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `time_end` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ship_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `phase` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `house_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `plot` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `latitude` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `longitude` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `site_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `site_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_address_full` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_sub_district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_sub_district_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_district_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_province` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_province_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_postal_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_country_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_map_url` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `nearby_landmark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_sale_order_delivery/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_sale_order_delivery`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_sale_order_delivery`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

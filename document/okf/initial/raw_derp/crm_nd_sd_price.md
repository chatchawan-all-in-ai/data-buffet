---
type: BigQuery Table
title: "crm_nd_sd_price"
description: "One row = one record of source table `crm_nd_sd_price` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_nd_sd_price&page=table"
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_nd_sd_price/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_nd_sd_price` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.crm_nd_sd_price](/validated/validated_derp/crm_nd_sd_price.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `nd_sd_price_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_barcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `effective_from` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `expiry_to` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `list_price_incl_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `list_price_excl_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `list_price_vat_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `floor_pct` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `floor_price_incl_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `nd_min_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `nd_max_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd1_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd1_rate_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd1_price_excl_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd1_min_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd1_max_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd2_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd2_rate_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd2_price_excl_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd2_min_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd2_max_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd3_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd3_rate_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd3_price_excl_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd3_min_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd3_max_qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bigpro_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bigpro_rate_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bigpro_price_excl_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deleted_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `floor_rate_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_nd_sd_price/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_nd_sd_price`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_nd_sd_price`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "product_detail"
description: "One row = one record of source table `product_detail` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=product_detail&page=table"
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

External table over AVRO files in `gs://file-raw-data/mastersku/product_detail/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `product_detail` table from MASTERSKU; nothing is cleaned or deduplicated here. Used by: [validated_mastersku.product_detail](/validated/validated_mastersku/product_detail.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `pd_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_prd_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_url_video` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_detail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_series` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_model` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_material` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_certificate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_garantee` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_garantee_detail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_shape` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_supplier_country` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_package_wide` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_package_long` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_package_hight` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_size_wide` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_size_long` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_sl_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_size_hight` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_sh_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_net_weight` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_gross_weight` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_uw_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_ul_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_uh_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_sw_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_net_unit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_gross_unit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_how_to` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_how_to_url` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_how_to_path` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_suggest` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_suggest_url` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_suggest_path` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_caution` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_caution_url` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_caution_path` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_file_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_file_path` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_is_system` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_created_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_updated_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_product_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_vendor_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_barcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_sale_unit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_spacific_fields` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pd_remark_inactive` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mastersku` (`definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mastersku/product_detail/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mastersku.product_detail`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mastersku.product_detail`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "product_detail"
description: "One row = one product detail record, a record of source table `product_detail` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=product_detail&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mastersku
table_id: product_detail
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

External table over AVRO files in `gs://file-raw-data/mastersku/product_detail/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `product_detail` table from MASTERSKU; nothing is cleaned or deduplicated here. Table meaning: Extended attributes of each MASTERSKU product: name, series, model, material, sizes, package dimensions, weights with units, warranty, TIS certificate and usage texts. Used by: [validated_mastersku.product_detail](/validated/validated_mastersku/product_detail.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `pd_id` | STRING | Unique identifier (UUID) of the product detail record. |
| `pd_prd_id` | STRING | Product this detail belongs to (FK to `product.prd_id`). |
| `pd_url_video` | STRING | URL of the product video. |
| `pd_detail` | STRING | Product description text (HTML). |
| `pd_series` | STRING | Product series name. |
| `pd_model` | STRING | Product model. |
| `pd_material` | STRING | Main material of the product (e.g. PE). |
| `pd_certificate` | STRING | Thai Industrial Standard (TIS) certificate of the product (e.g. `TIS.982-2556`). |
| `pd_garantee` | STRING | Warranty period of the product (e.g. `1Y`, `20 Y`). |
| `pd_garantee_detail` | STRING | Warranty terms and conditions text. |
| `pd_shape` | STRING | Packaging shape of the product (e.g. box, gallon, length). |
| `pd_supplier_country` | STRING | Country of the supplier (country of origin). |
| `pd_package_wide` | FLOAT64 | Package width. |
| `pd_package_long` | FLOAT64 | Package length. |
| `pd_package_hight` | FLOAT64 | Package height. |
| `pd_size_wide` | FLOAT64 | Product width. |
| `pd_size_long` | FLOAT64 | Product length (depth). |
| `pd_sl_id` | STRING | Unit of the product length `pd_size_long` (FK to `unit.unit_id`). |
| `pd_size_hight` | FLOAT64 | Product height. |
| `pd_sh_id` | STRING | Unit of the product height `pd_size_hight` (FK to `unit.unit_id`). |
| `pd_net_weight` | FLOAT64 | Net weight of the product. |
| `pd_gross_weight` | FLOAT64 | Gross (packed) weight of the product. |
| `pd_uw_id` | STRING | Unit of the package width `pd_package_wide` (FK to `unit.unit_id`). |
| `pd_ul_id` | STRING | Unit of the package length `pd_package_long` (FK to `unit.unit_id`). |
| `pd_uh_id` | STRING | Unit of the package height `pd_package_hight` (FK to `unit.unit_id`). |
| `pd_sw_id` | STRING | Unit of the product width `pd_size_wide` (FK to `unit.unit_id`). |
| `pd_net_unit_id` | STRING | Unit of the net weight (FK to `unit.unit_id`). |
| `pd_gross_unit_id` | STRING | Unit of the gross weight (FK to `unit.unit_id`). |
| `pd_how_to` | STRING | How-to-use text of the product (HTML). |
| `pd_how_to_url` | STRING | URL of the how-to-use document or media. |
| `pd_how_to_path` | STRING | Storage path of the how-to-use file. |
| `pd_suggest` | STRING | Usage recommendation text of the product (HTML). |
| `pd_suggest_url` | STRING | URL of the recommendation document or media. |
| `pd_suggest_path` | STRING | Storage path of the recommendation file. |
| `pd_caution` | STRING | Caution/warning text of the product (HTML). |
| `pd_caution_url` | STRING | URL of the caution document or media. |
| `pd_caution_path` | STRING | Storage path of the caution file. |
| `pd_file_name` | STRING | File name of the product image. |
| `pd_file_path` | STRING | Storage path of the product image file. |
| `pd_is_system` | BOOL | System flag of the product detail; TRUE together with the product active and in-use flags marks the product as approved. |
| `pd_created_date` | STRING | Timestamp when the record was created. |
| `pd_created_by` | STRING | Identifier of the user who created the record. |
| `pd_updated_date` | STRING | Timestamp when the record was last updated. |
| `pd_updated_by` | STRING | Identifier of the user who last updated the record. |
| `pd_product_name` | STRING | Full product name. |
| `pd_vendor_code` | STRING | Vendor own item code of the product. |
| `pd_barcode` | STRING | Barcode of the product. |
| `pd_sale_unit` | STRING | Sales unit of the product (e.g. `EA`). |
| `pd_spacific_fields` | STRING | Product-specific fields as JSON (`{"SpeciFeild":[{"label","value"}]}`). |
| `pd_remark_inactive` | STRING | Reason the product was made inactive (e.g. sale cancelled, duplicate). |
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

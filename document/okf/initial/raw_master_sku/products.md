---
type: BigQuery Table
title: "products"
description: "One row = one record of source table `products` (MASTER_SKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=products&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: products
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

External table over AVRO files in `gs://file-raw-data/master_sku/products/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `products` table from MASTER_SKU; nothing is cleaned or deduplicated here. Used by: [validated_master_sku.products](/validated/validated_master_sku/products.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sku_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `master_sku_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_size` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_style` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_color` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_configuration` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_variant` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `base_sku_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `universal_barcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `universal_barcode_history` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `internal_barcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `universal_barcode_format_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `internal_barcode_format_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `description_short` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `description` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `property` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `detail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `instruction` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `recommendation` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `caution` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `installation` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `transportation` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stack_over` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `warranty_detail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `warranty_period` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `shelf_life_period_days` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `tis_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `tis_permit_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `other_certification` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `net_weight` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `net_width` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `net_length` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `net_height` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `gross_weight` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `gross_width` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `gross_length` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `gross_height` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `weight_unit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `length_unit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `length_package_unit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `volume_unit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `volume` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_display_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_lowest_uom` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_conversion` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_sales_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_sales_conversion` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_sales_display_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_purchase_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_purchase_conversion` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_purchase_display_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_inventory_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_inventory_conversion` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_inventory_display_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_bom_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_bom_conversion` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uom_bom_display_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `search_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `tags` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `supplier_country` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `model` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `series` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `material` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `package_shape` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `shape` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `shade` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pattern` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `color_descriptor_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fob` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `business_unit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `brand_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `brand_vendor_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `category_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_type_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_sub_type_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `production_type_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `specification_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `specification_attributes` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cost_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `production_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `production_sale_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `marketing_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `purchase_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `account_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pricing_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_status_remark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_status_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `production_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `production_status_remark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `production_status_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_status_remark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_status_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `search_text` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `search_doc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/products/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.products`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_master_sku.products`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

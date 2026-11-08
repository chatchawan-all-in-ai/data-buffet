---
type: BigQuery Table
title: "product_channel_prices"
description: "One row = one product prices by sales channel, business unit, and effective date source record from MASTER_SKU, as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=product_channel_prices&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: product_channel_prices
tags: ["initial", "raw_master_sku", "master_sku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx"
    title: "Dataform definition (initial/master_sku/create_all_table_raw_master_sku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki: initial layer"
generated: { by: "agent:codex", at: "2026-11-08T22:49:49+07:00" }
status: draft
---



# What it is

External table over AVRO files in `gs://file-raw-data/master_sku/product_channel_prices/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of `product_channel_prices` from MASTER_SKU; no columns are cleaned or deduplicated here.

# Grain and key

One row per source record per ASATDATE partition. See the [validated table](../../validated/validated_master_sku/product_channel_prices.md#grain-and-key) for the deduplication key.

# Schema

| Column | Type | Description |
|---|---|---|
| `product_id` | STRING | Product identifier. |
| `sales_channel_id` | STRING | Sales channel identifier. |
| `business_unit_id` | STRING | Business unit identifier; nullable in the source. |
| `normal_discount_percent` | INT64 | Normal discount percent. |
| `special_discount_percent_1` | INT64 | First special discount percent. |
| `special_discount_percent_2` | INT64 | Second special discount percent. |
| `special_discount_percent_3` | INT64 | Third special discount percent. |
| `minimum_price` | FLOAT64 | Minimum price. |
| `minimum_discount` | FLOAT64 | Minimum discount. |
| `marketing_price` | FLOAT64 | Marketing price. |
| `effective_date` | STRING | Price effective date. |
| `expiration_date` | STRING | Price expiration date. |
| `status` | STRING | Source status. |
| `created_at` | STRING | UTC creation timestamp. |
| `created_by` | STRING | Creator identifier. |
| `updated_at` | STRING | UTC update timestamp. |
| `updated_by` | STRING | Updater identifier. |
| `ASATDATE` | STRING | Hive partition date (`YYYYMMDD`) of the GCS extract. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery; queries read the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/product_channel_prices/*`.
- Refresh: the extract job writes the files; the external table sees them without a Dataform refresh.

# Examples

Rows in a recent extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.product_channel_prices`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

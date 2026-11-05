---
type: BigQuery Table
title: "crm_sale_order_delivery"
description: "One row = one delivery round of a sale order, a record of source table `crm_sale_order_delivery` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order_delivery/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order_delivery` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Delivery rounds of DERP sale orders: delivery date, time window, receiver and delivery address.

Read by: [validated_derp.crm_sale_order_delivery](/validated/validated_derp/crm_sale_order_delivery.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_delivery_id` | STRING | Unique identifier of the sale order delivery round. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `so_date` | STRING | Date and time of the parent sale order. |
| `round_no` | INT64 | Delivery round number within the sale order, starting at 1. |
| `delivery_date` | STRING | Scheduled delivery date of the delivery round. |
| `delivery_address_id` | STRING | Identifier of the customer delivery address. |
| `delivery_address_code` | STRING | Customer code of the delivery address. |
| `delivery_address_text` | STRING | Delivery address text. |
| `receiver_name` | STRING | Name of the person receiving the goods. |
| `receiver_phone` | STRING | Phone number of the person receiving the goods. |
| `remark_logistic` | STRING | Remark for logistics. |
| `order_sort` | INT64 | Display order of the delivery round within its sale order, starting at 0. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `time_start` | STRING | Start time of the delivery time window (`HH:MM:SS`). |
| `time_end` | STRING | End time of the delivery time window (`HH:MM:SS`). |
| `ship_type` | STRING | Delivery destination type (`site` or `store`). |
| `phase` | STRING | Project phase of the delivery address. |
| `house_no` | STRING | House number of the delivery address. |
| `plot` | STRING | Plot number of the delivery address. |
| `latitude` | FLOAT64 | Latitude of the delivery address. |
| `longitude` | FLOAT64 | Longitude of the delivery address. |
| `site_id` | STRING | Identifier of the shipping site (plant or warehouse). |
| `site_code` | STRING | Code of the shipping site (plant or warehouse, e.g. `KTB`, `KK1`, `LP1`). |
| `delivery_address_full` | STRING | Full delivery address. |
| `delivery_sub_district` | STRING | Sub-district of the delivery address. |
| `delivery_sub_district_code` | STRING | Sub-district code of the delivery address. |
| `delivery_district` | STRING | District of the delivery address. |
| `delivery_district_code` | STRING | District code of the delivery address. |
| `delivery_province` | STRING | Province of the delivery address. |
| `delivery_province_code` | STRING | Province code of the delivery address. |
| `delivery_postal_code` | STRING | Postal code of the delivery address. |
| `delivery_country_code` | STRING | Country code of the delivery address (e.g. `THA`). |
| `delivery_map_url` | STRING | Map URL of the delivery address. |
| `nearby_landmark` | STRING | Nearby landmark of the delivery address. |
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

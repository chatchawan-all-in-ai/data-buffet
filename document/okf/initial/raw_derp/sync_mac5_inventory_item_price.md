---
type: BigQuery Table
title: "sync_mac5_inventory_item_price"
description: "One row = one synchronized item-price record, a record of source table `sync_mac5_inventory_item_price` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=sync_mac5_inventory_item_price&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: sync_mac5_inventory_item_price
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (definitions/initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:codex", at: "2026-11-08T22:03:22+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/sync_mac5_inventory_item_price/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `sync_mac5_inventory_item_price` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Synchronized D-ERP inventory item prices used by MAC5.

Read by: [validated_derp.sync_mac5_inventory_item_price](/validated/validated_derp/sync_mac5_inventory_item_price.md).

# Grain and key

One row per source record per `ASATDATE` partition. There is no key at this layer; see the [validated table card](../../validated/validated_derp/sync_mac5_inventory_item_price.md) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `item_number` | STRING | Item (product) number in the ERP item master. |
| `costing_version_id` | STRING | Costing version code (e.g. `STD` = standard cost). |
| `price_type` | STRING | Price type (e.g. `Cost`). |
| `from_date` | STRING | Date from which the price is effective. |
| `price_site_id` | STRING | Inventory site code (plant) the price applies to, e.g. `KTB`. |
| `product_configuration_id` | STRING | Product configuration dimension of the item. |
| `product_color_id` | STRING | Product color dimension of the item (e.g. `BK`, `GY`). |
| `product_size_id` | STRING | Product size dimension of the item (e.g. `01000L` = 1,000 litres). |
| `product_style_id` | STRING | Product style dimension of the item (e.g. `STDA`, `MALA`). |
| `product_version_id` | STRING | Product version dimension of the item. |
| `is_active` | STRING | Flag showing the record is active. |
| `price_created_datetime` | STRING | Timestamp when the price was created in the ERP. |
| `record_id` | INT64 | Record ID (RecId) of the price in the ERP. |
| `product_unit_symbol` | STRING | Unit of measure of the price (e.g. `PCS`). |
| `price_charges_quantity` | FLOAT64 | Quantity the price charges are expressed for. |
| `price_quantity` | FLOAT64 | Quantity the price is expressed for (price unit). |
| `price` | FLOAT64 | Item price (unit cost) in THB per price quantity. |
| `fixed_price_charges` | FLOAT64 | Fixed charges added to the price. |
| `calculation_number` | STRING | Cost calculation number that produced the price. |
| `is_price_including_charges` | STRING | Flag showing the price includes charges. |
| `created_datetime` | STRING | Timestamp when the record was created in the DERP extract. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_datetime` | STRING | Timestamp when the record was last updated in the DERP extract. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `inventory_item_price_id` | STRING | UUID of the item price record. |
| `ASATDATE` | STRING | Hive partition column (`YYYYMMDD`) identifying the extract date. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` preceded by `DROP TABLE IF EXISTS`.
- The external table stores metadata in BigQuery; queries read the GCS AVRO files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/sync_mac5_inventory_item_price/*`.
- The extract job writes files to the bucket; the external table sees them without a daily Dataform refresh.

# Examples

Rows from the latest extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.sync_mac5_inventory_item_price`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-level row counts by extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.sync_mac5_inventory_item_price`
GROUP BY ASATDATE
ORDER BY ASATDATE
```

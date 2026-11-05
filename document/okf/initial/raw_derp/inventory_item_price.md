---
type: BigQuery Table
title: "inventory_item_price"
description: "One row = one item price record per item, site and effective date, a record of source table `inventory_item_price` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=inventory_item_price&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: inventory_item_price
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

External table over AVRO files in `gs://file-raw-data/derp_temp/inventory_item_price/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `inventory_item_price` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Item cost prices (standard cost by site) from the ERP item price list, loaded from a daily full snapshot.

Read by: [validated_derp.inventory_item_price](/validated/validated_derp/inventory_item_price.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

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
| `inventory_item_price_id` | STRING | UUID of the item price record. |
| `created_datetime` | STRING | Timestamp when the record was created in the DERP extract. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_datetime` | STRING | Timestamp when the record was last updated in the DERP extract. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/inventory_item_price/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.inventory_item_price`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.inventory_item_price`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

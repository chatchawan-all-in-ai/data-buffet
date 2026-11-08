---
type: BigQuery Table
title: "sync_mac5_inventory_item_price"
description: "One row = one synchronized item-price record from source table `sync_mac5_inventory_item_price`, unique on (inventory_item_price_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=sync_mac5_inventory_item_price&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: sync_mac5_inventory_item_price
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/sync_mac5_inventory_item_price.sqlx"
    title: "Dataform definition (definitions/validated/derp/sync_mac5_inventory_item_price.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T22:03:22+07:00" }
status: draft
---

# What it is

Validated copy of DERP `sync_mac5_inventory_item_price`: every source field is cleaned or cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Synchronized D-ERP inventory item prices used by MAC5.

# Grain and key

One row per `inventory_item_price_id`. The key is declared in `uniqueKey` and `pk_key` and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `item_number` | STRING | Item (product) number in the ERP item master. |
| `costing_version_id` | STRING | Costing version code (e.g. `STD` = standard cost). |
| `price_type` | STRING | Price type (e.g. `Cost`). |
| `from_date` | DATE | Date from which the price is effective. |
| `price_site_id` | STRING | Inventory site code (plant) the price applies to, e.g. `KTB`. |
| `product_configuration_id` | STRING | Product configuration dimension of the item. |
| `product_color_id` | STRING | Product color dimension of the item (e.g. `BK`, `GY`). |
| `product_size_id` | STRING | Product size dimension of the item (e.g. `01000L` = 1,000 litres). |
| `product_style_id` | STRING | Product style dimension of the item (e.g. `STDA`, `MALA`). |
| `product_version_id` | STRING | Product version dimension of the item. |
| `is_active` | BOOL | Flag showing the record is active. |
| `price_created_datetime` | DATETIME | Timestamp when the price was created in the ERP. |
| `record_id` | INT64 | Record ID (RecId) of the price in the ERP. |
| `product_unit_symbol` | STRING | Unit of measure of the price (e.g. `PCS`). |
| `price_charges_quantity` | FLOAT64 | Quantity the price charges are expressed for. |
| `price_quantity` | FLOAT64 | Quantity the price is expressed for (price unit). |
| `price` | FLOAT64 | Item price (unit cost) in THB per price quantity. |
| `fixed_price_charges` | FLOAT64 | Fixed charges added to the price. |
| `calculation_number` | STRING | Cost calculation number that produced the price. |
| `is_price_including_charges` | BOOL | Flag showing the price includes charges. |
| `created_datetime` | DATETIME | Timestamp when the record was created in the DERP extract. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_datetime` | DATETIME | Timestamp when the record was last updated in the DERP extract. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `inventory_item_price_id` | STRING | UUID of the item price record. |
| `asatdate` | DATE | Extract date (`YYYY-MM-DD`), parsed from raw `ASATDATE` (`YYYYMMDD`); used for table partitioning. |

# How it is built

- Built by `definitions/validated/derp/sync_mac5_inventory_item_price.sqlx` as an incremental table partitioned on `asatdate` and clustered by the primary key.
- Reads the matching raw table, cleans or casts every source field, filters incremental runs to the configured backfill window, and keeps one row per key ordered by `updated_datetime DESC, asatdate DESC`.
- The primary key is added as `NOT ENFORCED` after full builds.

# Examples

Latest extract dates:

```sql
SELECT asatdate, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.sync_mac5_inventory_item_price`
GROUP BY asatdate
ORDER BY asatdate DESC
```

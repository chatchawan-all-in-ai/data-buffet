---
type: BigQuery Table
title: "inventory_movement_journal_entries"
description: "One row = one inventory movement journal line (latest version per journal number and line), a record of source table `inventory_movement_journal_entries` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=inventory_movement_journal_entries&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: inventory_movement_journal_entries
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

External table over AVRO files in `gs://file-raw-data/derp_temp/inventory_movement_journal_entries/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `inventory_movement_journal_entries` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Lines of ERP inventory movement journals (item, site, warehouse, quantity and cost per movement), mostly issues posted from MAC5 sales.

Read by: [validated_derp.inventory_movement_journal_entries](/validated/validated_derp/inventory_movement_journal_entries.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_movement_journal_entries_id` | STRING | UUID of this version of the journal line; the source issues a new UUID when the line is re-created, so the stable key is `journal_number` + `line_number`. |
| `movement_entries_id` | STRING | OData entity tag (ETag) of the journal line in the ERP. |
| `journal_number` | STRING | Inventory movement journal number (e.g. `IJ26-0224766`); links to the journal header. |
| `item_number` | STRING | Item (product) number in the ERP item master. |
| `product_configuration_id` | STRING | Product configuration dimension of the item. |
| `product_color_id` | STRING | Product color dimension of the item (e.g. `BK`, `GY`). |
| `product_size_id` | STRING | Product size dimension of the item (e.g. `01000L` = 1,000 litres). |
| `product_style_id` | STRING | Product style dimension of the item (e.g. `STDA`, `MALA`). |
| `inventory_site_id` | STRING | Inventory site code (plant), e.g. `HY1`, `KTB`. |
| `inventory_warehouse_id` | STRING | Warehouse code, e.g. `FG-HY1` (finished goods at site HY1). |
| `item_batch_number` | STRING | Batch number of the item. |
| `item_serial_number` | STRING | Serial number of the item unit. |
| `warehouse_location_id` | STRING | Warehouse location (bin) code, e.g. `HY1-CFG`. |
| `license_plate_number` | STRING | License plate (pallet or handling unit) number of the item. |
| `inventory_status_id` | STRING | Inventory status code (e.g. `A` = available). |
| `inventory_gtd_id` | STRING | Customs declaration (GTD) number dimension of the item. |
| `inventory_owner_id` | STRING | Inventory owner dimension of the item. |
| `inventory_profile_id` | STRING | Inventory profile dimension of the item. |
| `line_number` | FLOAT64 | Line number within the journal. |
| `fixed_cost_charges` | FLOAT64 | Fixed cost charges added to the line. |
| `inventory_quantity` | FLOAT64 | Quantity moved in inventory units (negative = issue, positive = receipt). |
| `unit_cost_quantity` | FLOAT64 | Quantity the unit cost is expressed for (price unit). |
| `cost_amount` | FLOAT64 | Total cost of the line (quantity x unit cost, negative for issues), in THB. |
| `transaction_date` | STRING | Date of the inventory transaction. |
| `offset_main_account_id_display_value` | STRING | Offset main (GL) account number of the line, e.g. `50100104`. |
| `default_ledger_dimension_display_value` | STRING | Financial (ledger) dimension string of the line, e.g. site, product group and cost-center segments. |
| `unit_cost` | FLOAT64 | Cost per unit of the item. |
| `catch_weight_quantity` | FLOAT64 | Catch-weight quantity of the movement. |
| `journal_name_id` | STRING | Journal name (journal type) code, e.g. `IM-MAC-01` for issues posted from MAC5. |
| `is_active` | STRING | Flag showing the record is active. |
| `remarks` | STRING | Free-text remarks. |
| `created_datetime` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_datetime` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `sync_hash` | STRING | MD5 hash of the record content, used by the extract to detect changed records. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/inventory_movement_journal_entries/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.inventory_movement_journal_entries`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.inventory_movement_journal_entries`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "inventory_movement_journal_entries"
description: "One row = one inventory movement journal line (latest version per journal number and line) from source table `inventory_movement_journal_entries`, unique on (journal_number, line_number)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=inventory_movement_journal_entries&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: inventory_movement_journal_entries
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/inventory_movement_journal_entries.sqlx"
    title: "Dataform definition (validated/derp/inventory_movement_journal_entries.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of DERP `inventory_movement_journal_entries`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Lines of ERP inventory movement journals (item, site, warehouse, quantity and cost per movement), mostly issues posted from MAC5 sales.
No other table or view in this repository reads it.

# Grain and key

One row per `journal_number`, `line_number`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_movement_journal_entries_id` | STRING | UUID of this version of the journal line; the source issues a new UUID when the line is re-created, so the stable key is `journal_number` + `line_number`. |
| `movement_entries_id` | STRING | OData entity tag (ETag) of the journal line in the ERP. |
| `journal_number` | STRING | Inventory movement journal number (e.g. `IJ26-0224766`); links to the journal header. |
| `journal_name_id` | STRING | Journal name (journal type) code, e.g. `IM-MAC-01` for issues posted from MAC5. |
| `line_number` | BIGNUMERIC | Line number within the journal. |
| `transaction_date` | DATE | Date of the inventory transaction. |
| `item_number` | STRING | Item (product) number in the ERP item master. |
| `product_configuration_id` | STRING | Product configuration dimension of the item. |
| `product_color_id` | STRING | Product color dimension of the item (e.g. `BK`, `GY`). |
| `product_size_id` | STRING | Product size dimension of the item (e.g. `01000L` = 1,000 litres). |
| `product_style_id` | STRING | Product style dimension of the item (e.g. `STDA`, `MALA`). |
| `inventory_site_id` | STRING | Inventory site code (plant), e.g. `HY1`, `KTB`. |
| `inventory_warehouse_id` | STRING | Warehouse code, e.g. `FG-HY1` (finished goods at site HY1). |
| `warehouse_location_id` | STRING | Warehouse location (bin) code, e.g. `HY1-CFG`. |
| `item_batch_number` | STRING | Batch number of the item. |
| `item_serial_number` | STRING | Serial number of the item unit. |
| `license_plate_number` | STRING | License plate (pallet or handling unit) number of the item. |
| `inventory_status_id` | STRING | Inventory status code (e.g. `A` = available). |
| `inventory_gtd_id` | STRING | Customs declaration (GTD) number dimension of the item. |
| `inventory_owner_id` | STRING | Inventory owner dimension of the item. |
| `inventory_profile_id` | STRING | Inventory profile dimension of the item. |
| `inventory_quantity` | FLOAT64 | Quantity moved in inventory units (negative = issue, positive = receipt). |
| `catch_weight_quantity` | FLOAT64 | Catch-weight quantity of the movement. |
| `unit_cost` | FLOAT64 | Cost per unit of the item. |
| `unit_cost_quantity` | FLOAT64 | Quantity the unit cost is expressed for (price unit). |
| `cost_amount` | FLOAT64 | Total cost of the line (quantity x unit cost, negative for issues), in THB. |
| `fixed_cost_charges` | FLOAT64 | Fixed cost charges added to the line. |
| `offset_main_account_id_display_value` | STRING | Offset main (GL) account number of the line, e.g. `50100104`. |
| `default_ledger_dimension_display_value` | STRING | Financial (ledger) dimension string of the line, e.g. site, product group and cost-center segments. |
| `is_active` | BOOL | Flag showing the record is active. |
| `remarks` | STRING | Free-text remarks. |
| `created_datetime` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_datetime` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `sync_hash` | STRING | MD5 hash of the record content, used by the extract to detect changed records. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/inventory_movement_journal_entries.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.inventory_movement_journal_entries](/initial/raw_derp/inventory_movement_journal_entries.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_datetime DESC, created_datetime DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `journal_number`, `line_number`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.inventory_movement_journal_entries`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT journal_number, line_number, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.inventory_movement_journal_entries`
GROUP BY journal_number, line_number
HAVING n > 1
```

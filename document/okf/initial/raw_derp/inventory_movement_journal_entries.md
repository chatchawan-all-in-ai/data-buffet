---
type: BigQuery Table
title: "inventory_movement_journal_entries"
description: "One row = one record of source table `inventory_movement_journal_entries` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=inventory_movement_journal_entries&page=table"
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/inventory_movement_journal_entries/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `inventory_movement_journal_entries` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.inventory_movement_journal_entries](/validated/validated_derp/inventory_movement_journal_entries.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_movement_journal_entries_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `movement_entries_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `journal_number` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `item_number` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_configuration_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_color_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_size_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_style_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inventory_site_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inventory_warehouse_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `item_batch_number` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `item_serial_number` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `warehouse_location_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `license_plate_number` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inventory_status_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inventory_gtd_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inventory_owner_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inventory_profile_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `line_number` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fixed_cost_charges` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inventory_quantity` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unit_cost_quantity` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cost_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `transaction_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `offset_main_account_id_display_value` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `default_ledger_dimension_display_value` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unit_cost` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `catch_weight_quantity` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `journal_name_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_active` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remarks` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_datetime` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_datetime` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sync_hash` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
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

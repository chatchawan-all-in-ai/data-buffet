---
type: BigQuery Table
title: "inventory_movement_journal_entries"
description: "One row = one cleaned copy of the source table `inventory_movement_journal_entries`, unique on (journal_number, line_number)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=inventory_movement_journal_entries&page=table"
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

Validated copy of DERP `inventory_movement_journal_entries`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `journal_number`, `line_number`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_movement_journal_entries_id` | STRING | Meaning not documented in the repo. |
| `movement_entries_id` | STRING | Meaning not documented in the repo. |
| `journal_number` | STRING | Meaning not documented in the repo. |
| `journal_name_id` | STRING | Meaning not documented in the repo. |
| `line_number` | BIGNUMERIC | Meaning not documented in the repo. |
| `transaction_date` | DATE | Meaning not documented in the repo. |
| `item_number` | STRING | Meaning not documented in the repo. |
| `product_configuration_id` | STRING | Meaning not documented in the repo. |
| `product_color_id` | STRING | Meaning not documented in the repo. |
| `product_size_id` | STRING | Meaning not documented in the repo. |
| `product_style_id` | STRING | Meaning not documented in the repo. |
| `inventory_site_id` | STRING | Meaning not documented in the repo. |
| `inventory_warehouse_id` | STRING | Meaning not documented in the repo. |
| `warehouse_location_id` | STRING | Meaning not documented in the repo. |
| `item_batch_number` | STRING | Meaning not documented in the repo. |
| `item_serial_number` | STRING | Meaning not documented in the repo. |
| `license_plate_number` | STRING | Meaning not documented in the repo. |
| `inventory_status_id` | STRING | Meaning not documented in the repo. |
| `inventory_gtd_id` | STRING | Meaning not documented in the repo. |
| `inventory_owner_id` | STRING | Meaning not documented in the repo. |
| `inventory_profile_id` | STRING | Meaning not documented in the repo. |
| `inventory_quantity` | FLOAT64 | Meaning not documented in the repo. |
| `catch_weight_quantity` | FLOAT64 | Meaning not documented in the repo. |
| `unit_cost` | FLOAT64 | Meaning not documented in the repo. |
| `unit_cost_quantity` | FLOAT64 | Meaning not documented in the repo. |
| `cost_amount` | FLOAT64 | Meaning not documented in the repo. |
| `fixed_cost_charges` | FLOAT64 | Meaning not documented in the repo. |
| `offset_main_account_id_display_value` | STRING | Meaning not documented in the repo. |
| `default_ledger_dimension_display_value` | STRING | Meaning not documented in the repo. |
| `is_active` | BOOL | Active flag from the source (inferred from the column name). |
| `remarks` | STRING | Meaning not documented in the repo. |
| `created_datetime` | DATETIME | Meaning not documented in the repo. |
| `created_by` | STRING | Meaning not documented in the repo. |
| `updated_datetime` | DATETIME | Meaning not documented in the repo. |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `sync_hash` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/inventory_movement_journal_entries.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.inventory_movement_journal_entries](/initial/raw_derp/inventory_movement_journal_entries.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_datetime DESC, created_datetime DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `journal_number`, `line_number`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,306,518 rows, 393.9 MB.

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

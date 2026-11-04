---
type: BigQuery Table
title: "inventory_movement_journal_headers"
description: "One row = one inventory movement journal header (latest version per journal number) from source table `inventory_movement_journal_headers`, unique on (journal_number)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=inventory_movement_journal_headers&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: inventory_movement_journal_headers
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/inventory_movement_journal_headers.sqlx"
    title: "Dataform definition (validated/derp/inventory_movement_journal_headers.sqlx)"
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

Validated copy of DERP `inventory_movement_journal_headers`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Headers of ERP inventory movement journals: journal type, default site and warehouse, and posting status.
No other table or view in this repository reads it.

# Grain and key

One row per `journal_number`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_movement_journal_headers_id` | STRING | UUID of this version of the journal header; the source issues a new UUID when the header is re-created, so the stable key is `journal_number`. |
| `movement_id` | STRING | OData entity tag (ETag) of the journal header in the ERP. |
| `journal_number` | STRING | Inventory movement journal number (e.g. `IJ26-0202167`). |
| `journal_name_id` | STRING | Journal name (journal type) code, e.g. `IM-MAC-01`, `IM-SP`, `IM-SCRAP`. |
| `description` | STRING | Journal description text (e.g. the source MAC5 issue document number and date). |
| `is_posted` | BOOL | Flag showing the journal has been posted. |
| `posted_datetime` | DATETIME | Timestamp when the journal was posted. |
| `posted_user_id` | STRING | User ID that posted the journal (e.g. `HY-S1`). |
| `default_inventory_site_id` | STRING | Default inventory site code (plant) for the journal lines, e.g. `KTB`, `HY1`. |
| `default_warehouse_id` | STRING | Default warehouse code for the journal lines, e.g. `FG-KTB`. |
| `reservation_mode` | STRING | Inventory reservation mode of the journal (e.g. `None`). |
| `posting_detail_level` | STRING | Level of detail used when posting the journal (e.g. `Detail`). |
| `voucher_number_selection_rule` | STRING | Rule for when a new voucher number is selected (e.g. `DateChange`). |
| `voucher_number_allocation_rule` | STRING | Rule for when the voucher number is allocated (e.g. `Post`). |
| `voucher_number_sequence_code` | STRING | Number sequence code used for voucher numbers (e.g. `IM-MAC-02`). |
| `are_lines_deleted_after_posting` | BOOL | Flag showing journal lines are deleted after posting. |
| `is_active` | BOOL | Flag showing the record is active. |
| `remarks` | STRING | Free-text remarks. |
| `created_datetime` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_datetime` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `sync_hash` | STRING | MD5 hash of the record content, used by the extract to detect changed records. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/inventory_movement_journal_headers.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.inventory_movement_journal_headers](/initial/raw_derp/inventory_movement_journal_headers.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_datetime DESC, created_datetime DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `journal_number`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.inventory_movement_journal_headers`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT journal_number, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.inventory_movement_journal_headers`
GROUP BY journal_number
HAVING n > 1
```

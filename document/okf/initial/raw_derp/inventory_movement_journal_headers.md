---
type: BigQuery Table
title: "inventory_movement_journal_headers"
description: "One row = one inventory movement journal header (latest version per journal number), a record of source table `inventory_movement_journal_headers` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=inventory_movement_journal_headers&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: inventory_movement_journal_headers
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

External table over AVRO files in `gs://file-raw-data/derp_temp/inventory_movement_journal_headers/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `inventory_movement_journal_headers` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Headers of ERP inventory movement journals: journal type, default site and warehouse, and posting status. Used by: [validated_derp.inventory_movement_journal_headers](/validated/validated_derp/inventory_movement_journal_headers.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_movement_journal_headers_id` | STRING | UUID of this version of the journal header; the source issues a new UUID when the header is re-created, so the stable key is `journal_number`. |
| `movement_id` | STRING | OData entity tag (ETag) of the journal header in the ERP. |
| `journal_number` | STRING | Inventory movement journal number (e.g. `IJ26-0202167`). |
| `is_posted` | STRING | Flag showing the journal has been posted. |
| `description` | STRING | Journal description text (e.g. the source MAC5 issue document number and date). |
| `default_warehouse_id` | STRING | Default warehouse code for the journal lines, e.g. `FG-KTB`. |
| `reservation_mode` | STRING | Inventory reservation mode of the journal (e.g. `None`). |
| `posting_detail_level` | STRING | Level of detail used when posting the journal (e.g. `Detail`). |
| `default_inventory_site_id` | STRING | Default inventory site code (plant) for the journal lines, e.g. `KTB`, `HY1`. |
| `journal_name_id` | STRING | Journal name (journal type) code, e.g. `IM-MAC-01`, `IM-SP`, `IM-SCRAP`. |
| `voucher_number_selection_rule` | STRING | Rule for when a new voucher number is selected (e.g. `DateChange`). |
| `posted_datetime` | STRING | Timestamp when the journal was posted. |
| `voucher_number_allocation_rule` | STRING | Rule for when the voucher number is allocated (e.g. `Post`). |
| `voucher_number_sequence_code` | STRING | Number sequence code used for voucher numbers (e.g. `IM-MAC-02`). |
| `are_lines_deleted_after_posting` | STRING | Flag showing journal lines are deleted after posting. |
| `posted_user_id` | STRING | User ID that posted the journal (e.g. `HY-S1`). |
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
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/inventory_movement_journal_headers/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.inventory_movement_journal_headers`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.inventory_movement_journal_headers`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

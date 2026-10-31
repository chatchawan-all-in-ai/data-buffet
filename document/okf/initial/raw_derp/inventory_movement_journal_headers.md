---
type: BigQuery Table
title: "inventory_movement_journal_headers"
description: "One row = one record of source table `inventory_movement_journal_headers` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=inventory_movement_journal_headers&page=table"
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

External table over AVRO files in `gs://file-raw-data/derp_temp/inventory_movement_journal_headers/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `inventory_movement_journal_headers` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.inventory_movement_journal_headers](/validated/validated_derp/inventory_movement_journal_headers.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_movement_journal_headers_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `movement_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `journal_number` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_posted` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `description` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `default_warehouse_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `reservation_mode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `posting_detail_level` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `default_inventory_site_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `journal_name_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `voucher_number_selection_rule` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `posted_datetime` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `voucher_number_allocation_rule` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `voucher_number_sequence_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `are_lines_deleted_after_posting` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `posted_user_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
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

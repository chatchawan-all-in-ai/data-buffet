---
type: BigQuery Table
title: "cdc_change_log"
description: "One row = one detected change (NEW or CHANGED) of one tracked source record on one day, comparing the raw table with the validated table."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=cdc_dataset&t=cdc_change_log&page=table"
project_id: databuffet-nonprd
dataset_id: cdc_dataset
table_id: cdc_change_log
tags: ["cdc", "mac5", "cdc_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/cdc/cdc_change_log.sqlx"
    title: "Dataform definition (cdc/cdc_change_log.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/cdc.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/cdc.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Change-data-capture log. Each day the operation compares the raw table of each CDC-enabled source table with its validated counterpart and writes a row for every record that is new in raw or whose configured check fields differ (after whitespace/trailing-punctuation normalization). Currently only `mac5.deb` (customer master; PKs `company_id`, `debcode`; check fields `debadd1at`, `debadd2at`, `debadd3at`, raw schema `raw_mac5_ag01`) is enabled, so the log tells which customer addresses changed. It exists for cost control: [deb_address_data](/process/deb_address_data.md) re-parses addresses with AI.GENERATE only for customers listed here for today.

Used by: [process_dataset.deb_address_data](/process/deb_address_data.md).

# Grain and key

One row per detected change per source record per day (`cdc_record_id` is a random `GENERATE_UUID()`; the stable record identity is `source_system` + `source_schema` + `source_table` + `pk_hash` / `pk_fields`). A day's rows are deleted and re-inserted on each run, so there is at most one row per record per `asatdate`. The table is partitioned by `asatdate`, clustered by `source_system, source_schema, source_table, change_type`, and keeps only 7 days (partition expiration).

# Schema

| Column | Type | Description |
|---|---|---|
| `cdc_record_id` | STRING | Random UUID (`GENERATE_UUID()`) identifying this log row; not stable across reruns. |
| `source_system` | STRING | Source name from `cdc-config.json` (currently 'mac5'). |
| `source_schema` | STRING | Validated dataset of the tracked table (config `validated_schema`, currently 'validated_mac5'). |
| `source_table` | STRING | Tracked table name (currently 'deb'). |
| `pk_fields` | JSON | JSON object of the primary-key values of the changed record, e.g. company_id and debcode (company_id is derived from the raw schema name, `raw_mac5_<company>`). |
| `pk_hash` | STRING | Hex MD5 of the comma-joined primary-key values (`TO_HEX(MD5(CONCAT(pk1, ',', pk2)))`), usable as a compact record key. |
| `change_type` | STRING | 'NEW' when the key does not exist in the validated table, 'CHANGED' when it exists and a check field differs. Unchanged records are not logged. |
| `asatdate` | DATE | Run date, `CURRENT_DATE('Asia/Bangkok')`; the partition column. |
| `change_timestamp` | TIMESTAMP | Timestamp when the change was recorded (`CURRENT_TIMESTAMP()` at insert). |
| `changed_fields` | JSON | JSON object mapping each changed check field name to `{raw, validated}` values (JSON-encoded strings); NULL for NEW rows. |
| `changed_field_names` | ARRAY<STRING> | Array of the check-field names that differ; NULL for NEW rows. |
| `num_fields_changed` | INT64 | Number of check fields that differ; 0 for NEW rows. |
| `record_raw` | JSON | The complete raw row as JSON. |
| `record_validated` | JSON | The complete validated row as JSON; NULL (JSON null) for NEW records. |
| `cdc_processed_at` | TIMESTAMP | Timestamp the CDC job processed the row (same as `change_timestamp` in practice). |

# How it is built

- Definition: `definitions/cdc/cdc_change_log.sqlx` (`type: "operations"`, tags `cdc`, `cdc_incremental`); the operation owns this table.
- Reads: [raw_mac5_ag01.deb](/initial/raw_mac5_ag01/deb.md), [validated_mac5.deb](/validated/validated_mac5/deb.md).
- Refresh: daily, `type: "operations"` script (tags `cdc`, `cdc_incremental`) generated at compile time from `includes/controller/cdc-config.json`: `CREATE TABLE IF NOT EXISTS` (partitioned, 7-day expiry), `DELETE` today's partition (idempotent rerun), then one INSERT per enabled table inside its own `BEGIN ... EXCEPTION` block; the run raises an error at the end if any table failed. Depends on `cdc_schema`. Tables with `partition_field = null` (like `deb`) are compared as full dumps; tables with a partition field read yesterday's raw partition and the latest validated version per key.

# Examples

Today's new and changed customer records (counts by type).

```sql
SELECT source_table, change_type, COUNT(*) AS changes
FROM `databuffet-nonprd.cdc_dataset.cdc_change_log`
WHERE asatdate = CURRENT_DATE('Asia/Bangkok')
GROUP BY source_table, change_type;
```

Which customer keys had address changes today (pattern used by deb_address_data).

```sql
SELECT JSON_VALUE(pk_fields, '$.company_id') AS company_id,
       JSON_VALUE(pk_fields, '$.debcode') AS debcode,
       change_type, changed_field_names
FROM `databuffet-nonprd.cdc_dataset.cdc_change_log`
WHERE source_system = 'mac5' AND source_schema = 'validated_mac5' AND source_table = 'deb'
  AND asatdate = CURRENT_DATE('Asia/Bangkok')
LIMIT 100;
```

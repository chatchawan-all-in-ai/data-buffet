---
type: BigQuery View
title: "export_status"
description: "One row = one ag01 document status code; commission set `status` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_status&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_status
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_status.sqlx"
    title: "Dataform definition (view/pub_sub/export_status.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-02T18:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `status` for the TF team (company ag01): one ag01 document status code. Its columns, names, order and JSON types are those of the commission sample sent to TF on 2026-10-14 (`commission_tf_ag01_2026`). The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `status` to topic `export-commission-status`. It is registered in [mart_export_config](/process/mart_export_config.md). First-load files of this set go under the export date (no `snapshot_date`).

# Grain and key

One ag01 document status code: key `company_source_id, id` (unique). `row_key` is the JSON of that key. Rows on 2026-11-02: 91.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of the source table. Part of the natural key. |
| `id` | INT64 | From `ar_scode` of the source table. Part of the natural key. |
| `status` | STRING | From `ar_snamet` of the source table. |
| `Active` | STRING | Constant '1' (as in the sample). |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(company_source_id, id))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL (a NULL key value is JSON null). |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_status.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Company `ag01` only; all rows.

# Examples

Rows per folder date of the first-load files (one folder: the export date).

```sql
SELECT CURRENT_DATE('Asia/Bangkok') AS folder_date, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_status`
GROUP BY folder_date
ORDER BY folder_date
```

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_status`
GROUP BY row_key
HAVING n > 1
```

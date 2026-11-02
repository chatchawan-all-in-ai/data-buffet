---
type: BigQuery View
title: "export_company_source"
description: "One row = the Data Mart company ag01 that owns the data; commission set `company_source` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_company_source&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_company_source
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_company_source.sqlx"
    title: "Dataform definition (view/pub_sub/export_company_source.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-02T18:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `company_source` for the TF team (company ag01): the Data Mart company ag01 that owns the data. Its columns, names, order and JSON types are those of the commission sample sent to TF on 2026-10-14 (`commission_tf_ag01_2026`). The Cloud Workflow `datamart-publish` compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `company_source` to topic `export-commission-company_source`. It is registered in [mart_export_config](/process/mart_export_config.md). First-load files of this set go under the export date (no `snapshot_date`).

# Grain and key

The Data Mart company ag01 that owns the data: key `company_source_id` (unique). `row_key` is the JSON of that key. Rows on 2026-11-02: 1.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `CompanyID` of the source table. Part of the natural key. |
| `CompanyCode` | STRING | From `CompanyCode` of the source table. |
| `CompanyNameTH` | STRING | From `CompanyNameTH` of the source table. |
| `CompanyNameEN` | STRING | From `CompanyNameEN` of the source table. |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(company_source_id))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL (a NULL key value is JSON null). |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_company_source.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_company](/dimension/dim_company.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Company `ag01` only; all rows.

# Examples

Rows per folder date of the first-load files (one folder: the export date).

```sql
SELECT CURRENT_DATE('Asia/Bangkok') AS folder_date, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_company_source`
GROUP BY folder_date
ORDER BY folder_date
```

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_company_source`
GROUP BY row_key
HAVING n > 1
```

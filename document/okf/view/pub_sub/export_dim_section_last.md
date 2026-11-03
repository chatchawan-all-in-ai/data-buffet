---
type: BigQuery View
title: "export_dim_section_last"
description: "One row = one sales section in its latest period, exposed for the Pub/Sub export of the AI team sample table dimension_table.dim_section_last with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_section_last&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_section_last
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_section_last.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_section_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_section_last](/dimension/dim_section_last.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Workflow `datamart-publish` compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `dim_section_last` to topic `export-ta-dim_section_last`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one sales section in its latest period: key `companyID`, `SectionID` (unique); `row_key` is the JSON of that key. Rows on 2026-11-02: 127.

# Schema

| Column | Type | Description |
|---|---|---|
| `SectionSK` | INT64 | Surrogate key of this snapshot, `ROW_NUMBER()` ordered by CompanySK, SectionID. Regenerated every run; not the same space as `dim_section.SectionSK`. |
| `SectionID` | STRING | Section code, from dim_section.SectionID. |
| `SectionName` | STRING | Section name from the kept interval. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_section_last.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_section_last](/dimension/dim_section_last.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `dimension_table.dim_section_last`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_section_last`
GROUP BY row_key
HAVING n > 1
```

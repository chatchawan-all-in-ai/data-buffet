---
type: BigQuery View
title: "export_positions"
description: "One row = one position held by someone in a company, exposed for the Pub/Sub export of the TA app table positions with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_positions&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_positions
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_positions.sqlx"
    title: "Dataform definition (view/pub_sub/export_positions.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-02T20:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `positions`: the distinct position codes that appear in [org_center_member](/org_center/org_center_member.md) per company (DIRECTOR, REGION_MGR, SECTION_MGR, TA, PC_MDT, PC_AGENT; CEO appears once someone holds it). The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `positions` to topic `export-ta-positions`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One position of one company: key `company_id, code` (unique). `row_key` is the JSON of the natural key. Rows on 2026-11-02: 10.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code. Part of the natural key. |
| `code` | STRING | Position code. Part of the natural key. |
| `name` | STRING | No source; always NULL. |
| `default_role_id` | STRING | No source; always NULL. |
| `uniform_code` | STRING | No source; always NULL. |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(<natural key>))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_positions.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_member](/org_center/org_center_member.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the org sample sent to the AI team on 2026-11-02 (one file per TA app table).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_positions`
GROUP BY row_key
HAVING n > 1
```

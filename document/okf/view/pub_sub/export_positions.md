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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `positions`: the distinct position codes that appear in [org_center_member](/org_center/org_center_member.md) per company; the possible codes are those of `org_center_member.position_code`. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-positions`.

# Grain and key

One row = one position of one company: key `company_id`, `code` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code. Part of the natural key. |
| `code` | STRING | Position code. Part of the natural key. |
| `name` | STRING | No source; always NULL. |
| `default_role_id` | STRING | No source; always NULL. |
| `uniform_code` | STRING | No source; always NULL. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_positions.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_member](/org_center/org_center_member.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_positions`
GROUP BY row_key
HAVING n > 1
```

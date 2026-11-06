---
type: BigQuery View
title: "export_sell"
description: "One row = one ag01 salesperson, hidden ones included; commission set `sell` for the TF team, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_sell&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_sell
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_sell.sqlx"
    title: "Dataform definition (view/pub_sub/export_sell.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `sell` for the TF team (company ag01): one ag01 salesperson, hidden ones included. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-commission-sell`.

# Grain and key

One row = one ag01 salesperson, hidden ones included: key `company_source_id`, `id` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of the source table. Part of the natural key. |
| `id` | STRING | From `percode` of the source table. Part of the natural key. |
| `sellid` | STRING | From `percode` of the source table. |
| `name` | STRING | From `pernamet` of the source table. |
| `surname` | STRING | Constant ''. |
| `position` | STRING | From `perpositn` of the source table. |
| `Sales_area` | STRING | From `perdep` of the source table. |
| `Sales_region` | STRING | Constant ''. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_sell.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.per](/validated/validated_mac5/per.md).

# Examples


Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_sell`
GROUP BY row_key
HAVING n > 1
```

---
type: BigQuery View
title: "export_view_dim_channel"
description: "One row = one sales channel of a company, exposed for the Pub/Sub export of dimension_view.view_dim_channel with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_channel&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_channel
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_channel.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_channel.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_channel](/view/dimension_view/view_dim_channel.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_channel`.

# Grain and key

One row = one sales channel of a company: key `companyID`, `DepCode` (unique); `row_key` is the JSON of that key. `companyID`, `DepCode` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `ChannelSK` | INT64 | Stable SK of the row in [dim_channel](/dimension/dim_channel.md). |
| `ChannelGroup` | STRING | Sales channel group name (pass-through from dim_channel). |
| `ChannelName` | STRING | Sales channel name (pass-through). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_channel.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_channel](/view/dimension_view/view_dim_channel.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_channel`
GROUP BY row_key
HAVING n > 1
```

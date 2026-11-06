---
type: BigQuery View
title: "export_dim_project"
description: "One row = one project profile, exposed for the Pub/Sub export of dimension_table.dim_project with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_project&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_project
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_project.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_project.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_project](/dimension/dim_project.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_project`.

# Grain and key

One row = one project profile: key `ProjectSK` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProjectSK` | INT64 | Stable surrogate key; never regenerated. |
| `companyName` | STRING | Company name of the project owner or contractor. |
| `place` | STRING | Location of the project. |
| `district` | STRING | District of the project. |
| `province` | STRING | Province of the project. |
| `companyStatus` | STRING | Project status colour (`เขียว` = green, `เหลือง` = yellow, `แดง` = red). |
| `profileComp` | STRING | Project profile description (e.g. condominium, hotel). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_project.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_project](/dimension/dim_project.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_project`
GROUP BY row_key
HAVING n > 1
```

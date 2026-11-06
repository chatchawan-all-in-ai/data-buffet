---
type: BigQuery View
title: "export_dim_company"
description: "One row = one company, exposed for the Pub/Sub export of the table dimension_table.dim_company with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_company&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_company
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_company.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_company.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:27:50+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_company](/dimension/dim_company.md), with the business columns of the company dimension under their dim names (no surrogate key, no MdsId), for the whole table. After each successful `dim_company` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_company`.

# Grain and key

One row = one company: key `CompanyID` (unique); `row_key` is the JSON of that key. `CompanyID` is never NULL in `dim_company`.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanyID` | STRING | Company code (e.g. ag01) from `dim_company.CompanyID`; the natural key of the export and `primary_key` of the Pub/Sub message. |
| `CompanyCode` | STRING | Company code/short name from `dim_company.CompanyCode`. |
| `CompanyNameTH` | STRING | Company name in Thai from `dim_company.CompanyNameTH`. |
| `CompanyNameEN` | STRING | Company name in English from `dim_company.CompanyNameEN`. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_company.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_company](/dimension/dim_company.md).

# Examples

What would be published for all companies.

```sql
SELECT CompanyID, CompanyCode, CompanyNameTH, CompanyNameEN, row_key, row_hash
FROM `databuffet-nonprd.pub_sub.export_dim_company`
ORDER BY CompanyID
```

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_company`
GROUP BY row_key
HAVING n > 1
```

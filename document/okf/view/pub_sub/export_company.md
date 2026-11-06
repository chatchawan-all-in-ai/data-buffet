---
type: BigQuery View
title: "export_company"
description: "One row = one ag01 customer; commission set `company` for the TF team, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_company&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_company
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_company.sqlx"
    title: "Dataform definition (view/pub_sub/export_company.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-05T16:27:42+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `company` for the TF team (company ag01): one ag01 customer. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-commission-company`.

# Grain and key

One row = one ag01 customer: key `company_source_id`, `id` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of the source table. Part of the natural key. |
| `id` | STRING | From `debcode` of the source table. Part of the natural key. |
| `companyname` | STRING | From `debnamet` of the source table. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_company.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.deb](/validated/validated_mac5/deb.md).

# Examples


Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_company`
GROUP BY row_key
HAVING n > 1
```

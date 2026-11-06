---
type: BigQuery View
title: "export_brand"
description: "One row = one product brand, exposed for the Pub/Sub export of validated_mastersku.brand with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_brand&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_brand
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_brand.sqlx"
    title: "Dataform definition (view/pub_sub/export_brand.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [validated_mastersku.brand](/validated/validated_mastersku/brand.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-brand`.

# Grain and key

One row = one product brand: key `bra_id` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `bra_id` | STRING | Unique identifier (UUID) of the brand. |
| `bra_name` | STRING | Brand name. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_brand.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mastersku.brand](/validated/validated_mastersku/brand.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_brand`
GROUP BY row_key
HAVING n > 1
```

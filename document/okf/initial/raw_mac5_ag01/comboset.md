---
type: BigQuery Table
title: "comboset"
description: "One row = one item in a combo set, a record of source table `comboset` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=comboset&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: comboset
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/comboset/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `comboset` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Items that make up each combo set, with quantity and list price. Used by: [validated_mac5.comboset](/validated/validated_mac5/comboset.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Running ID of the combo set line row. |
| `combostk` | STRING | Combo set code the line belongs to (joins `combostk.combostk`). |
| `stkcode` | STRING | Stock code of the item in the combo set. |
| `date` | STRING | Date and time the row was created. |
| `uinsert` | STRING | User code of the person who created the record. |
| `uupdate` | STRING | User code of the person who last updated the record. |
| `status` | INT64 | Status code of the combo set line (1 = active). |
| `quantity` | INT64 | Quantity of the item in the combo set. |
| `price` | FLOAT64 | Price of the item in the combo set. |
| `lp` | FLOAT64 | List price of the item. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/comboset/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.comboset`
LIMIT 100
```

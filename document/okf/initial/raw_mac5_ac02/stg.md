---
type: BigQuery Table
title: "stg"
description: "One row = one stock group, a record of source table `stg` (MAC5 for company `ac02`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ac02&t=stg&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ac02
table_id: stg
tags: ["initial", "raw_mac5_ac02", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_ac02.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_ac02.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ac02/stg/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `stg` table from MAC5 for company `ac02`; nothing is cleaned or deduplicated here. Table meaning: Stock group master with Thai/English names and the mapped accounting product group.

Read by: [validated_mac5.stg](/validated/validated_mac5/stg.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `stgcode` | STRING | Stock group code. |
| `stgdesct` | STRING | Thai name of the stock group. |
| `stgdesce` | STRING | English name or type label of the stock group. |
| `rowguid` | STRING | Row GUID that uniquely identifies the record in the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ac02` (`definitions/initial/mac5/create_all_table_raw_mac5_ac02.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ac02/stg/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ac02.stg`
LIMIT 100
```

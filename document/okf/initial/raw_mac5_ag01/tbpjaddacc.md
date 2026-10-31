---
type: BigQuery Table
title: "tbpjaddacc"
description: "One row = one record of source table `tbpjaddacc` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbpjaddacc&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbpjaddacc
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbpjaddacc/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbpjaddacc` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.tbpjaddacc](/validated/validated_mac5/tbpjaddacc.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pjid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `accid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `accname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `acctype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `acctype2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `accpow` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `conid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `conname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `condetail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `insertdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `textnote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `nickname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `religion` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `birthdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lineidper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `emailper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `idcardper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `addressper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `country` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `province` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sub_district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `zipcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `spousefullname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `birthdatespouse` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `numberofchildren` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `favoriteactivity` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unfavoriteactivity` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `trait` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbpjaddacc/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbpjaddacc`
LIMIT 100
```

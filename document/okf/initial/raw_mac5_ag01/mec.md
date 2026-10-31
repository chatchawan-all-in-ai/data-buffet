---
type: BigQuery Table
title: "mec"
description: "One row = one record of source table `mec` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mec&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: mec
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mec/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `mec` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.mec](/validated/validated_mac5/mec.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `MECcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECtpl` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECtoCType` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECtoCode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECd1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECd2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECd3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECi1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECi2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECc1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECc2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECc3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECc4` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECc5` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm7` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm8` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECm9` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECdesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MEChide` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MEClock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECeditLK` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECrefWE` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECsortN` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt7` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt8` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt9` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECt10` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECeditDT` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `MECeditMF` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mec/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mec`
LIMIT 100
```

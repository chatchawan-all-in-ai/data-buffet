---
type: BigQuery Table
title: "ttrip"
description: "One row = one record of source table `ttrip` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=ttrip&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: ttrip
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

External table over AVRO files in `gs://file-raw-data/mac5_gps/ttrip/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `ttrip` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.ttrip](/validated/validated_mac5/ttrip.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `frun` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fmaster` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fvehicle` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fother` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fprice` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fbuddy` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fdeduct_detail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fdeduct_monkey` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fdeduct_money` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ftype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fcomplete` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `foil` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fpass_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fpay` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `foil_deduct` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `loadip` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `loadvnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fremark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `flitre_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `flitre` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fcubic` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_gps/ttrip/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.ttrip`
LIMIT 100
```

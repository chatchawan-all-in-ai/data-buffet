---
type: BigQuery Table
title: "cre"
description: "One row = one record of source table `cre` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cre&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: cre
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cre/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `cre` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.cre](/validated/validated_mac5/cre.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `crecode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cregroup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crenamet` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crenamee` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crecontactt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crecontacte` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creadd1at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creadd2at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creadd3at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creadd1ae` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creadd2ae` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creadd3ae` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cretel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cretaxnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crezone` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cregrade` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crelimit` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cretaxclass` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cregoodsdef` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crecreditterm` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crehide` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crefax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creemail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cretarget` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crememo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creac` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crelock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creoname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creprice` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creeditlk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crerefwe` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cresortnt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cresortne` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crecardid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creeditdt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creeditmf` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cretaxtype` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creinex` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crebranch` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cre/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cre`
LIMIT 100
```

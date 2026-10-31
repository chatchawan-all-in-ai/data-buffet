---
type: BigQuery Table
title: "per"
description: "One row = one record of source table `per` (MAC5 for company `aa05`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_aa05&t=per&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_aa05
table_id: per
tags: ["initial", "raw_mac5_aa05", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_aa05.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_aa05.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_aa05/per/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `per` table from MAC5 for company `aa05`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.per](/validated/validated_mac5/per.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `percode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perdep` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pertaxnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pernamet` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pernamee` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perbdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perworks` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perworkf` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `peradd1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `peradd2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `peradd3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pertel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perpositn` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pernchild` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `percisstudy` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pernotstudy` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `persalary` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perhide` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perlock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `permemo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pereditlk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `perrefwe` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pereditdt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pereditmf` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_aa05` (`definitions/initial/mac5/create_all_table_raw_mac5_aa05.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_aa05/per/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_aa05.per`
LIMIT 100
```

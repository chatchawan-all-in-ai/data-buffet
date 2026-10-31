---
type: BigQuery Table
title: "dep"
description: "One row = one record of source table `dep` (MAC5 for company `ab01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ab01&t=dep&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ab01
table_id: dep
tags: ["initial", "raw_mac5_ab01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_ab01.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_ab01.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ab01/dep/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `dep` table from MAC5 for company `ab01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.dep](/validated/validated_mac5/dep.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `depcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `depgroup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `depdesct` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `depdesce` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dephide` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deplock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `depeditdt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `depeditmf` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ab01` (`definitions/initial/mac5/create_all_table_raw_mac5_ab01.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ab01/dep/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ab01.dep`
LIMIT 100
```

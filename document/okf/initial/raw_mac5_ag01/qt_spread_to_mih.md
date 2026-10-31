---
type: BigQuery Table
title: "qt_spread_to_mih"
description: "One row = one record of source table `qt_spread_to_mih` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=qt_spread_to_mih&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: qt_spread_to_mih
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/qt_spread_to_mih/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `qt_spread_to_mih` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.qt_spread_to_mih](/validated/validated_mac5/qt_spread_to_mih.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qt_spread_ref_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qtid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihvnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rdysendtomac5` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/qt_spread_to_mih/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.qt_spread_to_mih`
LIMIT 100
```

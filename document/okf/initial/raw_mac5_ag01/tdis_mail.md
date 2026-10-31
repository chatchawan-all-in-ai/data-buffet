---
type: BigQuery Table
title: "tdis_mail"
description: "One row = one record of source table `tdis_mail` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tdis_mail&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tdis_mail
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tdis_mail/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tdis_mail` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.tdis_mail](/validated/validated_mac5/tdis_mail.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `saleid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `spass` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `salename` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `salemail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mail1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mail2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mail3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mail4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lv` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc7` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc8` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cc9` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `passlv1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `passlv2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `passlv3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `passlv4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f7` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f8` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f9` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `f10` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pum1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pum2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pum3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ppass1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ppass2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ppass3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ma` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ta` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ceo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `app` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lv_pum` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lv_rp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rp1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rp2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rp3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rpass1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rpass2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rpass3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lv_ele` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ele1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ele2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ele3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `epass1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `epass2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `epass3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `menu1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `download` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pic` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lv_boq_lyn` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `active` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tdis_mail/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tdis_mail`
LIMIT 100
```

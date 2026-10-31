---
type: BigQuery Table
title: "main_qtspread"
description: "One row = one record of source table `main_qtspread` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=main_qtspread&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: main_qtspread
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/main_qtspread/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `main_qtspread` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.main_qtspread](/validated/validated_mac5/main_qtspread.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qtid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `atten` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lat` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `long` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mapnote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `city` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ctel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ctel2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `road` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `area` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `postcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `caddress` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `podocno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rdosend` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `checknote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `checknote2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `checknote3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `checknote4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `checknotemoney` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `textnote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `editnote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `editnotedate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delvdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `transferfg` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `meccode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `subcontract` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `blueprint` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `projectname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihjob` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `repeatblueprint` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `noteblueprint` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discountthreepercent` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `paybycash` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `creditterm` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `moneydeposit` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `extrasum` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `agent` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `termpayment` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `discountcash` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `paytype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `refer_order_allkons_m` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `etax` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `etax_email` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/main_qtspread/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.main_qtspread`
LIMIT 100
```

---
type: BigQuery Table
title: "deb"
description: "One row = one record of source table `deb` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=deb&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/deb/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `deb` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.deb](/validated/validated_mac5/deb.md), [cdc_dataset.cdc_change_log](/cdc/cdc_change_log.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `debcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debgroup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debnamet` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debnamee` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcontactt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcontacte` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debadd1at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debadd2at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debadd3at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debadd1ae` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debadd2ae` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debadd3ae` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debtel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debtaxnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debzone` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debgrade` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deblimit` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debtaxclass` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debgoodsdef` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcreditterm` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpaytype` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayday` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayon1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayon2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayon3` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayon4` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayon5` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayn1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debpayn2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbgrtype` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbgrday` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbgron1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbgron2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbgron3` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbgron4` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbgron5` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debhide` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debfax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debemail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debtarget` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debmemo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debac` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deblock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deboname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm7` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm8` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm9` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debcm10` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debprice` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debeditlk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debrefwe` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbillad` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debsortnt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debsortne` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debeditdt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debeditmf` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debinex` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debsalesp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbranch` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debxxxx` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbusinesstype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debbusinessdesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debactive` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `debexpiredate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/deb/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.deb`
LIMIT 100
```

---
type: BigQuery Table
title: "vmp"
description: "One row = one record of source table `vmp` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=vmp&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/vmp/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `vmp` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.vmp](/validated/validated_mac5/vmp.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `VMmonth` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMyear` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLtotal` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb3` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb4` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb5` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb6` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb7` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb8` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb9` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb10` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb11` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb12` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb13` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb14` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb15` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb16` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb17` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb18` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb19` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb20` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb21` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb22` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb23` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb24` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb25` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb26` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb27` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb28` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb29` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb30` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb31` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb32` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb33` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb34` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb35` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb36` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb37` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb38` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb39` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb40` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb41` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb42` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb43` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb44` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb45` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb46` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb47` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb48` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb49` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMGLb50` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARtotal` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARquo` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARpo` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARdel` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARbil` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARinv` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARdrn` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARcrn` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARcash` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARlease` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMARrec` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPtotal` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPquo` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPpo` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPdel` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPbil` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPinv` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPdrn` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPcrn` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPcash` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPlease` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMAPrec` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICtotal` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICgin` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICgout` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICgrt` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICgrf` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICjour` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICmstr` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMICpr` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMPRtotal` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMPRsalary` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `VMPRmemo` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/vmp/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.vmp`
LIMIT 100
```

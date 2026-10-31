---
type: BigQuery Table
title: "stk"
description: "One row = one record of source table `stk` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=stk&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: stk
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/stk/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `stk` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.stk](/validated/validated_mac5/stk.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `STKcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKgroup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKcode2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKdescT1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKdescT2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKdescT3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKdescE1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKdescE2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKdescE3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKmax` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKmin` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKunit1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKunit2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKconv1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKconv2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKsnsv` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKuname0` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKuname1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKuname2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKuname3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKuname4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKuname5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqU1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqU2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqU3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqU4` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqU5` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqE1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqE2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqE3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqE4` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqE5` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqN1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqN2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqN3` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqN4` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKqN5` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKvat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKexpire` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKhide` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKuse2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKu2name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKfx` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKacP` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKacS` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKacC` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKlock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKmemo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKacC1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKacC2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKeditLK` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKrefWE` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKbarC1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKbarC2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKbarC3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKsortNT` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKsortNE` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKeditDT` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKsto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKeditMF` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKcode885` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKtype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKSaleGrp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKSaleType` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKSaleSup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKSaleGrpS1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKSaleGrpS2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `StkSub1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `StkSub2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `StkSub3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `StkBrand` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `StkExpand` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `StkLgGrp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKgroup_DGE` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKgroup1_DGE_Report` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKgroup2_DGE_Report` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `STKgroup3_DGE_Report` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Part_DGE` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `StkFPASS` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/stk/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.stk`
LIMIT 100
```

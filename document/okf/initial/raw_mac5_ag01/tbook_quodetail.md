---
type: BigQuery Table
title: "tbook_quodetail"
description: "One row = one record of source table `tbook_quodetail` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbook_quodetail&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbook_quodetail
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbook_quodetail/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbook_quodetail` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.tbook_quodetail](/validated/validated_mac5/tbook_quodetail.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `linkid` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkdesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quantity` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lp` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `nd` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sd3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dispercent` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `crc` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `priceforag` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `com` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `setcb` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sent` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `datepart` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fg` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pic` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `productcp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pricecp` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `giveaway` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `givestk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bgcount` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `orderno` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lat` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `long` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mapnote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fileupload` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `city` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rdosend` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ctel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `caddress` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `checknote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `textnote` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_quodetail` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `productgrade` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fobprice` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `isshow` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbook_quodetail/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbook_quodetail`
LIMIT 100
```

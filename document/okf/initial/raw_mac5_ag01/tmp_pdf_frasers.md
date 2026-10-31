---
type: BigQuery Table
title: "tmp_pdf_frasers"
description: "One row = one record of source table `tmp_pdf_frasers` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tmp_pdf_frasers&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tmp_pdf_frasers/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tmp_pdf_frasers` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.tmp_pdf_frasers](/validated/validated_mac5/tmp_pdf_frasers.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `crdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vendorno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vendorname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `newpo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pono` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `podate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `potype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deliverydate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `siteno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sitename` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `siteaddress` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `totalqty` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `totalamount` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `totalitem` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cancelpo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `termcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `poremark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotationno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotationdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `poitemno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `artno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `artdesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `hpeancode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vdeancode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vdproductname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qty` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `purchunit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `price` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qtyperunit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `priceperunit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `priceunit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `packsize` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `articleremark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `freegoodsflag` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `novat` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `attfile` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `statusticket` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `duedate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `reciver` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deladd` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `que` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delvname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delvtel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tmp_pdf_frasers/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tmp_pdf_frasers`
LIMIT 100
```

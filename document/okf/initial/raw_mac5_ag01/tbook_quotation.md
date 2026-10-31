---
type: BigQuery Table
title: "tbook_quotation"
description: "One row = one record of source table `tbook_quotation` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbook_quotation&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbook_quotation/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbook_quotation` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.tbook_quotation](/validated/validated_mac5/tbook_quotation.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `running` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `atten` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `address` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `price_validity` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `termdelivery` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `termpayment` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `agent1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `agent2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `period` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `disc` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `extrasum` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `extradesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `date1st` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `date1end` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `date2st` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `date2end` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cashstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `note` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `noteforapp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `memoforapp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rev` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `typecus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `channel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `channel2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `typeprice` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fob` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cancel` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `apptype` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `typedeb` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `saledep` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `typeproject` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `selectstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `conpostatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
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
| `statusspread` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `chkbox` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fobstt` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotation_ref` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_group` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotation_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `estatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `area` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `postcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qtstepprice` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `extradis` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbook_quotation/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbook_quotation`
LIMIT 100
```

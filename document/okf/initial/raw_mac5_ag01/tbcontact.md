---
type: BigQuery Table
title: "tbcontact"
description: "One row = one record of source table `tbcontact` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbcontact&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbcontact/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbcontact` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.tbcontact](/validated/validated_mac5/tbcontact.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpersonal` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactcompany` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactcop` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsegment` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactchannel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactstatus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contacttitle` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactnick` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactaddress` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactaddress1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactaddress2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactaddress3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactaddress4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactaddress5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactaddress6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contacttel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactmail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contacttype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactbday` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactage` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactbyear` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contacthob` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactstudy` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactmag` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactme` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactcolor` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactfood` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactlife` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactact` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsday` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactdesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactlove` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactson` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactcntson` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactcntgirl` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonname1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonage1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonstudy1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonname2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonage2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonstudy2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonname3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonage3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactsonstudy3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactposition` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpower` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `projectcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpp1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpp2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpp3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpp4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpp5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpp6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `insertby` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `insertwhen` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lastupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactpath20` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactdebcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `activestatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `lineidcorp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbcontact/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbcontact`
LIMIT 100
```

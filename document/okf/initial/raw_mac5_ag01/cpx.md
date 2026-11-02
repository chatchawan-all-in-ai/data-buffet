---
type: BigQuery Table
title: "cpx"
description: "One row = one outstanding internal request line, a record of source table `cpx` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cpx&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: cpx
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cpx/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `cpx` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Outstanding internal request (`PX`) lines: requested versus issued quantity, with clearing flags. Used by: [validated_mac5.cpx](/validated/validated_mac5/cpx.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `cpxstkid` | STRING | Product (stock) code of the outstanding request line, matching `stk.stkcode`. |
| `cpxlinkid` | INT64 | Internal ID linking the outstanding record to its document line. |
| `cpxvnosid` | STRING | Number of the internal request (`PX`) document that has the outstanding line. |
| `cpxdateid` | STRING | Date of the internal request document. |
| `cpxjob` | STRING | Job code of the document (sales job or project category). |
| `cpxdep` | STRING | Department code of the document, used as the sales channel code. |
| `cpxper` | STRING | Requesting employee code of the document. |
| `cpxdoc` | STRING | Document reference code. |
| `cpxmec` | STRING | Memo-card code of the document, matching `mec.meccode`. |
| `cpxsto` | STRING | Warehouse (store) code the request is issued from. |
| `cpxstkreq` | FLOAT64 | Quantity requested on the line. |
| `cpxstkcut` | FLOAT64 | Quantity already issued against the request line. |
| `cpxclearstk` | INT64 | Flag: outstanding quantity cleared (-1 = cleared). |
| `cpxclearuser` | INT64 | Flag: line cleared manually by a user (-1 = yes). |
| `cpxclearall` | INT64 | Flag: line fully cleared (-1 = cleared). |
| `cpxstatus` | INT64 | Status code of the outstanding line. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cpx/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cpx`
LIMIT 100
```

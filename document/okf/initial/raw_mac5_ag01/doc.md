---
type: BigQuery Table
title: "doc"
description: "One row = one document type, a record of source table `doc` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=doc&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: doc
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/doc/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `doc` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Document type master of the MAC5 ERP: code, Thai/English name, group and default GL account.

Read by: [validated_mac5.doc](/validated/validated_mac5/doc.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `DOCcode` | STRING | Document type code (e.g. `PO`, `POL`, `FR`). |
| `DOCgroup` | STRING | Document group code (e.g. `A`, `P`, `S`, `AR`, `AK`). |
| `DOCdescT` | STRING | Thai name of the document type. |
| `DOCdescE` | STRING | English name of the document type. |
| `DOClock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `DOCacc` | STRING | Default GL account code of the document type (e.g. `110100`). |
| `DOCdebit` | INT64 | Debit-side flag of the document type (-1 = debit, 0 = not). |
| `DOCrefWE` | STRING | External reference code of the record. |
| `DOChide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `DOCeditDT` | STRING | Date and time the record was last edited. |
| `DOCeditMF` | STRING | User code of the person who last edited the record. |
| `rowguid` | STRING | Row GUID that uniquely identifies the record in the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/doc/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.doc`
LIMIT 100
```

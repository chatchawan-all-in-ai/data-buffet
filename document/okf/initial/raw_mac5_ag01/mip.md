---
type: BigQuery Table
title: "mip"
description: "One row = one file attached to a document, a record of source table `mip` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mip&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: mip
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mip/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `mip` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Files attached to ERP documents (purchase orders, maps, BOQs, quotations), one row per document, file number and revision.

Read by: [validated_mac5.mip](/validated/validated_mac5/mip.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `mipvnos` | STRING | Number of the document the file is attached to. |
| `mipfileno` | INT64 | Sequence number of the attached file within the document. |
| `miprev` | INT64 | Revision number of the attachment. |
| `mippath` | STRING | File path or file name of the attachment. |
| `miptype` | STRING | Attachment type code (e.g. `POD`, `MAP`, `BOQ`, `QOD`, `ETC`). |
| `mipcrdate` | STRING | Date and time the attachment was created. |
| `mipupdatedate` | STRING | Date and time the attachment was last updated. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mip/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mip`
LIMIT 100
```

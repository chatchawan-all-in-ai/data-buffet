---
type: BigQuery Table
title: "maincontract"
description: "One row = one main contractor, a record of source table `maincontract` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=maincontract&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: maincontract
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/maincontract/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `maincontract` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Main contractors (developers), identified by their MAC5 customer code. Used by: [validated_mac5.maincontract](/validated/validated_mac5/maincontract.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `mcontractid` | STRING | MAC5 customer (debtor) code of the main contractor (developer). |
| `dateinsert` | STRING | Date and time the row was created. |
| `status` | INT64 | Active flag (1 = active). |
| `uinsert` | STRING | Employee code of the user who created the row. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/maincontract/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.maincontract`
LIMIT 100
```

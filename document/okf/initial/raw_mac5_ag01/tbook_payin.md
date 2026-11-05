---
type: BigQuery Table
title: "tbook_payin"
description: "One row = one pay-in record of a sales order, a record of source table `tbook_payin` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbook_payin&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbook_payin
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbook_payin/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbook_payin` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Pay-in submissions of sales orders with status and approval time.

Read by: [validated_mac5.tbook_payin](/validated/validated_mac5/tbook_payin.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `orderno` | STRING | MAC5 sales order number the pay-in belongs to. |
| `status` | INT64 | Pay-in status code (0 to 6). |
| `datetime` | STRING | Date and time the pay-in was submitted. |
| `datetimeapprove` | STRING | Date and time the pay-in was approved. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbook_payin/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbook_payin`
LIMIT 100
```

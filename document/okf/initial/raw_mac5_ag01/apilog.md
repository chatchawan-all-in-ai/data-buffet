---
type: BigQuery Table
title: "apilog"
description: "One row = one API job run, a record of source table `apilog` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=apilog&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: apilog
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/apilog/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `apilog` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Run log of the API job that processes Allkons orders, with start and end time, success flag, message and processed orders. Used by: [validated_mac5.apilog](/validated/validated_mac5/apilog.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `logid` | INT64 | Run identifier of the API job. |
| `runat` | STRING | Date and time the API run started. |
| `completedat` | STRING | Date and time the API run finished. |
| `issuccess` | INT64 | Success flag of the run (1 = success, 0 = failed). |
| `errormessage` | STRING | Error or status message of the run (e.g. `Batch is null - no orders to process.`). |
| `resultjson` | STRING | JSON array of the orders processed in the run, keyed by Allkons billing number. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/apilog/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.apilog`
LIMIT 100
```

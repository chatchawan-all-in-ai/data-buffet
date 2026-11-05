---
type: BigQuery Table
title: "ap_s"
description: "One row = one AP document status, a record of source table `ap_s` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=ap_s&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: ap_s
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/ap_s/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `ap_s` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Status codes and display names (with colours) for purchase-side documents, referenced by `mihstatus`. Used by: [validated_mac5.ap_s](/validated/validated_mac5/ap_s.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `ap_scode` | INT64 | AP (purchase) document status code, referenced by `mihstatus` of purchase documents. |
| `ap_snamet` | STRING | Thai status name. |
| `ap_snamee` | STRING | English status name (often the same Thai text). |
| `ap_scolf` | INT64 | Foreground (text) colour of the status in the ERP, as a Windows RGB integer. |
| `ap_scolb` | INT64 | Background colour of the status in the ERP, as a Windows RGB integer. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/ap_s/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.ap_s`
LIMIT 100
```

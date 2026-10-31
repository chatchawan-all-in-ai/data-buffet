---
type: BigQuery Table
title: "cpp"
description: "One row = one record of source table `cpp` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cpp&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cpp/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `cpp` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.cpp](/validated/validated_mac5/cpp.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `cppstkid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpplinkid` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppvnosid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppdateid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppcusid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppjob` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppdep` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppdoc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppmec` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppsto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppstkreq` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppstkcut1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppstkcut2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppsumreq` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppsumcut1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppsumcut2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppclearstk` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppclearsum` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppclearuser` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppclearall` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppcurc` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppexchg` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppcut` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cppdelvdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpplistno` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cpp/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cpp`
LIMIT 100
```

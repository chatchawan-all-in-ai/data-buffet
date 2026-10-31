---
type: BigQuery Table
title: "tbook_profilecomp"
description: "One row = one record of source table `tbook_profilecomp` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbook_profilecomp&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbook_profilecomp
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbook_profilecomp/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbook_profilecomp` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.tbook_profilecomp](/validated/validated_mac5/tbook_profilecomp.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `docno` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `projectcode` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `projectname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `statuscomp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `compname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `register` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `addresscomp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `province` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `country` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `capital` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `place` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mobile` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `fax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `namedirector` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `nickname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `teldirector` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `profilecomp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `typecomp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `startdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `history` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pjstart` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pjend` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pjval` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pjfor` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `compgroup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `acccode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `accname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `closedby` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `projectfrom` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ptype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ppc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pecom` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dinsert` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `insertby` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `uupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dupdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `meccode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `contactdebcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `refallkon` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbook_profilecomp/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbook_profilecomp`
LIMIT 100
```

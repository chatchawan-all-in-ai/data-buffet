---
type: BigQuery Table
title: "cst"
description: "One row = one record of source table `cst` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cst&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cst/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `cst` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.cst](/validated/validated_mac5/cst.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `cstdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `csttype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstvnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstcus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cststk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstjob` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstdep` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstdoc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstmec` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cststo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstquan` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstquanp2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstcogsp` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstexpdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstlinkvc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstlinkvcid` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstio` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstiozw` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstlist` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstcosta` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstcostf` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cstcostl` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cst/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cst`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.cst`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

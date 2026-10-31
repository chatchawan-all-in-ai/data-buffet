---
type: BigQuery Table
title: "cps"
description: "One row = one record of source table `cps` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cps&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cps/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `cps` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.cps](/validated/validated_mac5/cps.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `cpsstkid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpslinkid` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsvnosid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsdateid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpscusid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsjob` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsdep` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsdoc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsmec` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpssto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsstkreq` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsstkcut1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsstkcut2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpssumreq` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpssumcut1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpssumcut2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsclearstk` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsclearsum` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsclearuser` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsclearall` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpscurc` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsexchg` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpscut` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpsdelvdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cpslistno` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cps/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cps`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.cps`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

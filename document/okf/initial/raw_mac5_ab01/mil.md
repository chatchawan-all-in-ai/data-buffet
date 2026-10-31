---
type: BigQuery Table
title: "mil"
description: "One row = one record of source table `mil` (MAC5 for company `ab01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ab01&t=mil&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ab01
table_id: mil
tags: ["initial", "raw_mac5_ab01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_ab01.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_ab01.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ab01/mil/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mil` table from MAC5 for company `ab01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.mil](/validated/validated_mac5/mil.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `milday` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milmonth` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milyear` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miltype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milvnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milcus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milstk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miljob` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mildep` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mildoc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milmec` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milsto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milstomt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `millistno` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milquan` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milquanp2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miladisc` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milcog` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milconv` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mildisca` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mildisct` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milvat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milsum` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milcut` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milstype` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miluname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mildesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milvcol1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milvcol2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milvcol3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milvcol4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milcurc` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milexchg` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milacost` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milpqm` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milpmfrom` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milpmto` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miltag` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `millinkvcno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `millinkvcdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `millinkvctype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `millinkvcdeposit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `millinkvcid` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milclearum` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milexpdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milnotes` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milnotkl` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mildelvdt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mildatesp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milnumcsp` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milnumisp` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milcost` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milucost` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miluprice` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milusequanp` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milvcol5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `milfitem` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ab01` (`definitions/initial/mac5/create_all_table_raw_mac5_ab01.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ab01/mil/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ab01.mil`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ab01.mil`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "mih_dummy"
description: "One row = one record of source table `mih_dummy` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mih_dummy&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: mih_dummy
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mih_dummy/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mih_dummy` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.mih_dummy](/validated/validated_mac5/mih_dummy.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `mihday` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihmonth` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihyear` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihtype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihvnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihcus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihjob` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdep` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihper` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdoc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihmec` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihvatno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdesc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihmemo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihnotes` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihref1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihref2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihref3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdischt1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdischt2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdelvsite` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdelvdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihstanding` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihlinkgl` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihnouplink` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihnolist` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihcurc` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihvatinlist` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihlock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihprintn` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihcheque` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihcancel` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihclearum` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihctermno` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihcog` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihvatsum` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihnetsum` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdisclst` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdischf1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdischf2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihexchg` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihextrasum` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihextravat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihextracut` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihextramem` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihrecno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihrecdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihsavetag` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihkeyuser` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihkeydate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdocrunno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdategl` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihduepo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miheditlk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihiscf` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihissp` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdates1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihdates2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihnumsi` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihnumsc` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihvatpc` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihincluded` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihtaxvnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihtaxdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihtaxsum` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihload` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihpaiddate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihbookordernum` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihsenddate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihbl` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihrpv` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihclearcut` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mihsettlecut` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mih_dummy/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mih_dummy`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.mih_dummy`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "rcv"
description: "One row = one record of source table `rcv` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=rcv&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/rcv/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `rcv` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.rcv](/validated/validated_mac5/rcv.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `serial` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvtype` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvvnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvstk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `descT1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qty` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvsto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `username` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvtime` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Fdatetime2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvStatus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvtypeFG` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvstatusMR` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvzone` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvOrder` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvCommand` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvExtCode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mixVnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mixDate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvTranCode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvCancel` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvOrder_Pack` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `adjVnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `PackDate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `PackTime` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rcvConvert` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Odate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Ouser` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `FMIL2LISTNO` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Ostatus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/rcv/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.rcv`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.rcv`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

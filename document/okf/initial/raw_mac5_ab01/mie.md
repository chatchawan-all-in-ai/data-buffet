---
type: BigQuery Table
title: "mie"
description: "One row = one record of source table `mie` (MAC5 for company `ab01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ab01&t=mie&page=table"
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

External table over AVRO files in `gs://file-raw-data/mac5_ab01/mie/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mie` table from MAC5 for company `ab01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.mie](/validated/validated_mac5/mie.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `mieday` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miemonth` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mieyear` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mietype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mievnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miecus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdt3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdt53` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdrnd` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdexg` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdcsh` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdoth` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecplus` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miereccash` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miereccqrd` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miectermcx` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miectermpx` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miectermax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miectermdx` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mietag` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miebasedt3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miebasedt53` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miedescdt3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miedescdt53` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miecondt3` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miecondt53` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecfc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdt32` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mierecdt532` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miebasedt32` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miebasedt532` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miedescdt32` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miedescdt532` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miecondt32` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `miecondt532` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mieperdt3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mieperdt32` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mieperdt53` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mieperdt532` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mietaxpayno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ab01` (`definitions/initial/mac5/create_all_table_raw_mac5_ab01.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ab01/mie/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ab01.mie`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ab01.mie`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

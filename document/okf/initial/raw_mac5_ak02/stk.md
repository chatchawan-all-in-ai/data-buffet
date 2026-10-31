---
type: BigQuery Table
title: "stk"
description: "One row = one record of source table `stk` (MAC5 for company `ak02`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ak02&t=stk&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ak02
table_id: stk
tags: ["initial", "raw_mac5_ak02", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_ak02.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_ak02.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ak02/stk/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `stk` table from MAC5 for company `ak02`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.stk](/validated/validated_mac5/stk.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `stkcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkgroup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkcode2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkdesct1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkdesct2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkdesct3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkdesce1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkdesce2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkdesce3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkmax` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkmin` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkunit1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkunit2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkconv1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkconv2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stksnsv` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkuname0` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkuname1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkuname2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkuname3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkuname4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkuname5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqu1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqu2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqu3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqu4` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqu5` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqe1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqe2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqe3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqe4` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqe5` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqn1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqn2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqn3` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqn4` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkqn5` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkvat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkexpire` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkhide` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkuse2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stku2name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkfx` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkacp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkacs` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkacc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stklock` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkmemo` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkacc1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkacc2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkeditlk` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkrefwe` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkbarc1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkbarc2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkbarc3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stksortnt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stksortne` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkeditdt` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stksto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stkeditmf` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ak02` (`definitions/initial/mac5/create_all_table_raw_mac5_ak02.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ak02/stk/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ak02.stk`
LIMIT 100
```

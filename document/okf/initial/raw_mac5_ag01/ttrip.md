---
type: BigQuery Table
title: "ttrip"
description: "One row = one delivery trip, a record of source table `ttrip` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=ttrip&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: ttrip
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

External table over AVRO files in `gs://file-raw-data/mac5_gps/ttrip/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `ttrip` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Delivery trips of the GPS delivery app, with vehicle, release time and trip costs. Used by: [validated_mac5.ttrip](/validated/validated_mac5/ttrip.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `frun` | STRING | Trip identifier (timestamp `yyMMddHHmmss` plus sequence), referenced by `ttrip_document.fmaster` and `tdelivery.fmaster`. |
| `fmaster` | STRING | Master reference of the trip. |
| `fcode` | STRING | Trip code (document number of the trip). |
| `fdate` | STRING | Date and time the trip was created (`yyyyMMddHHmmss`). |
| `fvehicle` | STRING | Vehicle registration plate of the trip. |
| `fother` | STRING | Other note of the trip. |
| `fprice` | INT64 | Trip price. |
| `fbuddy` | INT64 | Helper (buddy) allowance amount of the trip. |
| `fdeduct_detail` | STRING | Deduction detail of the trip. |
| `fdeduct_monkey` | FLOAT64 | Deduction amount of the trip (misspelled duplicate of `fdeduct_money`). |
| `fdeduct_money` | FLOAT64 | Deduction amount of the trip. |
| `ftype` | STRING | Trip type code. |
| `fcomplete` | STRING | Trip completion flag. |
| `foil` | STRING | Fuel rate code of the trip. |
| `fpass_date` | STRING | Date and time the vehicle was released for the trip (`yyyyMMddHHmmss`). |
| `fpay` | STRING | Paid flag of the trip (1 = paid). |
| `foil_deduct` | INT64 | Fuel deduction value of the trip. |
| `loadip` | INT64 | Load IP flag. |
| `loadvnos` | STRING | Loading document number. |
| `fremark` | STRING | Trip remark, such as the distance driven. |
| `flitre_price` | FLOAT64 | Fuel price value of the trip. |
| `flitre` | FLOAT64 | Fuel quantity value of the trip. |
| `fcubic` | FLOAT64 | Cubic volume loaded on the trip. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_gps/ttrip/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.ttrip`
LIMIT 100
```

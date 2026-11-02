---
type: BigQuery Table
title: "cql"
description: "One row = one cheque ledger entry, a record of source table `cql` (MAC5 for company `aa05`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_aa05&t=cql&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_aa05
table_id: cql
tags: ["initial", "raw_mac5_aa05", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_aa05.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_aa05.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_aa05/cql/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `cql` table from MAC5 for company `aa05`; nothing is cleaned or deduplicated here. Table meaning: Cheque and bank-book ledger entries linking each cheque to the receipt or payment document it settles. Used by: [validated_mac5.cql](/validated/validated_mac5/cql.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `cqldate` | STRING | Date of the cheque ledger entry. |
| `cqlbank` | STRING | Bank code of the cheque (e.g. `BBL`, `KBANK`). |
| `cqlno` | STRING | Cheque number, matching `chq.chqno`. |
| `cqlsys` | INT64 | Source system of the entry (1 = bank book, 2 = receipt or payment document). |
| `cqlday` | INT64 | Day part of the entry date. |
| `cqlmonth` | INT64 | Month part of the entry date. |
| `cqlyear` | INT64 | Year part of the entry date (Gregorian). |
| `cqlbook` | INT64 | Bank book number (0 = entry linked to a receipt or payment document). |
| `cqlvnos` | STRING | Number of the receipt or payment document the cheque settles (e.g. `RI-...`). |
| `cqlsuml` | FLOAT64 | Cheque amount of the entry. |
| `cqlmivt` | STRING | Document type of the linked document (RS = receipt, RP = payment, `--` = none). |
| `cqlcus` | STRING | Customer code (supplier code for payments), matching `deb.debcode`. |
| `cqltag` | INT64 | Tag marker of the entry. |
| `cqlautono` | INT64 | Auto-increment ID of the entry. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_aa05` (`definitions/initial/mac5/create_all_table_raw_mac5_aa05.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_aa05/cql/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_aa05.cql`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_aa05.cql`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

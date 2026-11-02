---
type: BigQuery Table
title: "mir"
description: "One row = one receipt or billing statement line, a record of source table `mir` (MAC5 for company `ak02`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ak02&t=mir&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ak02
table_id: mir
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

External table over AVRO files in `gs://file-raw-data/mac5_ak02/mir/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mir` table from MAC5 for company `ak02`; nothing is cleaned or deduplicated here. Table meaning: Lines of receipts (`RS`/`RP`) and billing statements (`VS`/`VP`), each settling or billing one invoice or note. Used by: [validated_mac5.mir](/validated/validated_mac5/mir.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `mirday` | INT64 | Day part of the document date. |
| `mirmonth` | INT64 | Month part of the document date. |
| `miryear` | INT64 | Year part of the document date (Gregorian). |
| `mirtype` | STRING | Document type code (RS = sales receipt, VS = sales billing statement; RP / VP on the purchase side). |
| `mirvnos` | STRING | Receipt or billing-statement document number. |
| `mircus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `mirlistno` | INT64 | Line number within the receipt or billing statement. |
| `mirbinvno` | STRING | Number of the invoice (or debit/credit note) settled or billed by this line. |
| `mirbinvdate` | STRING | Date of the invoice settled or billed by this line. |
| `mirbinvtype` | STRING | Document type of the invoice settled or billed by this line (IS, AS, BS). |
| `mirdesc` | STRING | Description copied from the referenced invoice. |
| `mircog` | FLOAT64 | Line amount excluding VAT. |
| `mirvat` | FLOAT64 | VAT amount of the line. |
| `mirsum` | FLOAT64 | Line amount including VAT (amount received or billed). |
| `mircurc` | INT64 | Currency code (0 = Thai baht). |
| `mirexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `mirtag` | INT64 | Tag marker of the line. |
| `mirnotes` | STRING | Notes copied from the referenced invoice. |
| `miraccount` | STRING | Account code of the line. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ak02` (`definitions/initial/mac5/create_all_table_raw_mac5_ak02.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ak02/mir/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ak02.mir`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ak02.mir`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

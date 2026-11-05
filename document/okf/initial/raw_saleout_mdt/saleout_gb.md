---
type: BigQuery Table
title: "saleout_gb"
description: "One row = one product line of one Global House bill, a record of source table `saleout_gb` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=saleout_gb&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: saleout_gb
tags: ["initial", "raw_saleout_mdt", "saleout"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx"
    title: "Dataform definition (initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/saleout_mdt/gb/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `saleout_gb` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Daily sell-out bill lines of the company products at Global House branches, including returns.

Read by: [validated_saleout_mdt.saleout_gb](/validated/validated_saleout_mdt/saleout_gb.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `No_` | STRING | Line number of the row in the report file. |
| `Sale_No_` | STRING | Global House bill (sales document) number. |
| `Sale_Date` | STRING | Sale (bill) date. |
| `Branch_Code` | STRING | Global House branch code (e.g. `GH-218`). |
| `Branch_Name` | STRING | Global House branch name. |
| `Branch_Short_Name` | STRING | Short branch abbreviation used in bill numbers. |
| `Product_Code` | STRING | Global House product code (13-digit barcode). |
| `Product_Name` | STRING | Product name. |
| `Sale_Quantity` | INT64 | Sales quantity (negative = return). |
| `Sale_Amount` | STRING | Sales amount (THB; negative = return). |
| `Type` | STRING | Document type: `SALE` or `RETURN` (newer files send Thai `ขาย`/`รับคืน`). |
| `Reference_No_` | STRING | Original bill number referenced by a return. |
| `Deposit_No_` | STRING | Deposit document number linked to the bill. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/gb/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.saleout_gb`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.saleout_gb`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

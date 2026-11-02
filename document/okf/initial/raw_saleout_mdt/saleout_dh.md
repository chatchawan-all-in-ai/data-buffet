---
type: BigQuery Table
title: "saleout_dh"
description: "One row = one product, branch, sale date and sale/return flag, a record of source table `saleout_dh` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=saleout_dh&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: saleout_dh
tags: ["initial", "raw_saleout_mdt", "saleout"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx"
    title: "Dataform definition (initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/saleout_mdt/dh/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `saleout_dh` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Daily sell-out of the company products at DoHome branches, from monthly SharePoint files (latest file per zone and month). Used by: [validated_saleout_mdt.saleout_dh](/validated/validated_saleout_mdt/saleout_dh.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `SALES_DATE` | STRING | Sale date. |
| `BRANCH_CODE` | STRING | DoHome branch code (`M...` = DoHome To Go branches). |
| `PRODUCT_CODE` | STRING | DoHome product code (not a barcode). |
| `PRODUCT_NAME` | STRING | Product name. |
| `SALES_QTY` | FLOAT64 | Sales quantity (negative = return). |
| `SALES_AMOUNT` | FLOAT64 | Sales amount (THB; negative = return). |
| `SOURCE_FOLDER` | STRING | SharePoint folder (DoHome sales zone) the file came from. |
| `FILE_MODIFIED` | STRING | Last-modified timestamp text of the source file before validated selection of the latest file per folder and month. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/dh/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.saleout_dh`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.saleout_dh`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

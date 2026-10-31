---
type: BigQuery Table
title: "eom_tw"
description: "One row = one record of source table `eom_tw` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=eom_tw&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: eom_tw
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/so_mdt_eom/tw/reportsalesubscriptionmonth/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `eom_tw` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Used by: [curated_saleout_mdt.curated_eom_tw](/curated/curated_saleout_mdt/curated_eom_tw.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `PERIOD` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Store` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Cat` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Sub_Cat` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Brand` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `SKU` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Barcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Description` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Product_Type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Sales_Amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Sales_Qty` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Stock_On_Hand` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Stock_On_Order` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Last_Sold_Date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `Last_Receive_Date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/so_mdt_eom/tw/reportsalesubscriptionmonth/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.eom_tw`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.eom_tw`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

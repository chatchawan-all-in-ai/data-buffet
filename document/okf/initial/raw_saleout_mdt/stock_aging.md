---
type: BigQuery Table
title: "stock_aging"
description: "One row = one article age band at one Boonthavorn branch on one snapshot date, a record of source table `stock_aging` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=stock_aging&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: stock_aging
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/bt/stock_aging/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `stock_aging` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Stock aging report from Boonthavorn (BT): stock quantity and value of the company products by branch, article and age band, with stock class.

Read by: [validated_saleout_mdt.stock_aging](/validated/validated_saleout_mdt/stock_aging.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `VENDOR_ID` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `VENDOR_NAME` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `BRANCH` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `ARTICLE_ID` | STRING | Boonthavorn article (product) code. |
| `ARTICLE_NAME_TH` | STRING | Product name in Thai. |
| `BRAND` | STRING | Product brand. |
| `MCH3` | STRING | Boonthavorn merchandise category, top level (department). |
| `MCH2` | STRING | Boonthavorn merchandise category, second level. |
| `TILE_SIZE` | FLOAT64 | Tile size of the article (tile products only). |
| `ITEM_FLAG` | STRING | Item movement flag (`REGULAR`, `FAST`, `DISCON` = discontinued). |
| `AGING_TIER` | STRING | Stock age band (`1) 0 - 60 Days` to `8) >361 Days`). |
| `CLASS_STOCK` | STRING | Boonthavorn stock class (`B3G Class A`, `B3G Class B`, `B3G Class C`, `B3G New`, `B3G Dead`). |
| `AGING` | INT64 | Stock age in days. |
| `UR_AMT` | FLOAT64 | Value of the unrestricted stock in this age band (THB). |
| `UR_QTY` | INT64 | Unrestricted stock quantity in this age band. |
| `RESERVE_AMT` | FLOAT64 | Value of the stock reserved for orders (THB). |
| `RESERVE_QTY` | INT64 | Stock quantity reserved for orders. |
| `REMAIN_AMT` | FLOAT64 | Value of the stock remaining after reservations (THB). |
| `REMAIN_QTY` | INT64 | Stock quantity remaining after reservations. |
| `START_DATE` | STRING | Stock snapshot date (same as `end_date`). |
| `END_DATE` | STRING | Stock snapshot date. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/bt/stock_aging/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.stock_aging`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.stock_aging`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

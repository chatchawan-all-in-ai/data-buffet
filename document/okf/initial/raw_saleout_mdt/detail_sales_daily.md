---
type: BigQuery Table
title: "detail_sales_daily"
description: "One row = one article, branch and sales channel on one sale date, a record of source table `detail_sales_daily` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=detail_sales_daily&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: detail_sales_daily
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/bt/detail_sales_daily/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `detail_sales_daily` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Boonthavorn (BT) daily sell-out of the company products per branch, article and channel (format used from 2026-10-08). Used by: [validated_saleout_mdt.detail_sales_daily](/validated/validated_saleout_mdt/detail_sales_daily.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `Vendor_Id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `Vendor_Name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `DATE_ID` | STRING | Sale date (`YYYY-MM-DD`). |
| `Sales_Office` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `Sales_Channel` | STRING | Sales channel at Boonthavorn (`Showroom`, `Anyhome`, `Web`). |
| `Article_Id` | STRING | Boonthavorn article (product) code. |
| `Article_Name_Th` | STRING | Product name in Thai. |
| `Brand` | STRING | Product brand. |
| `MCH3_Desc` | STRING | Boonthavorn merchandise category, top level (department). |
| `MCH2_Desc` | STRING | Boonthavorn merchandise category, second level. |
| `MCH1_Desc` | STRING | Boonthavorn merchandise category, third level. |
| `MC_Desc` | STRING | Boonthavorn merchandise category, lowest level. |
| `Item_Flag` | STRING | Item movement flag (`REGULAR`, `FAST`, `DISCON` = discontinued). |
| `Flag_Project` | STRING | Project-sale flag (`Project`/`Non-Project`). |
| `SALE_NET_INC` | FLOAT64 | Net sales amount for the day including VAT (THB). |
| `SALE_QTY` | INT64 | Sales quantity for the day. |
| `SALE_SQM` | FLOAT64 | Sales in square metres for the day. |
| `Vendor_Article` | STRING | Product code of the company (vendor) for the article; can be empty. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/bt/detail_sales_daily/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.detail_sales_daily`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.detail_sales_daily`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

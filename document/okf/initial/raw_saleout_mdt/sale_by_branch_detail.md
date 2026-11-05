---
type: BigQuery Table
title: "sale_by_branch_detail"
description: "One row = one article, branch and sales channel for one report date, a record of source table `sale_by_branch_detail` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=sale_by_branch_detail&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: sale_by_branch_detail
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/bt/sale_by_branch_detail/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `sale_by_branch_detail` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Boonthavorn (BT) sell-out file with month-to-date (MTD) sales of the company products per branch, article and channel; curated derives daily sales from the change in MTD values.

Read by: [validated_saleout_mdt.sale_by_branch_detail](/validated/validated_saleout_mdt/sale_by_branch_detail.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `VENDOR_ID` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `VENDOR_NAME` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `YEAR_DATE_ID` | INT64 | Year of the report period. |
| `MONTH_DATE_ID` | STRING | Month name of the report period in English (e.g. `July`). |
| `BRANCH` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `DISTRIBUTION_CHANNEL` | STRING | Source sales-channel text at Boonthavorn, including Website before its validated renaming to Web. |
| `ARTICLE_ID` | STRING | Boonthavorn article (product) code. |
| `ARTICLE_NAME_TH` | STRING | Product name in Thai. |
| `BRAND` | STRING | Product brand. |
| `FLAG_PROJECT` | STRING | Project-sale flag (`Y`/`N`; daily file sends `Project`/`Non-Project`). |
| `ITEM_FLAG` | STRING | Item movement flag (`REGULAR`, `FAST`, `DISCON` = discontinued). |
| `MCH3` | STRING | Boonthavorn merchandise category, top level (department). |
| `MCH2` | STRING | Boonthavorn merchandise category, second level. |
| `NET_INC_TAX` | FLOAT64 | Month-to-date net sales amount including VAT (THB). |
| `SALE_QTY` | INT64 | Month-to-date sales quantity. |
| `SALE_SQM` | FLOAT64 | Month-to-date sales in square metres. |
| `START_DATE` | STRING | First day of the reporting period. |
| `END_DATE` | STRING | Last day covered by the report (figures are counted up to this date). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/bt/sale_by_branch_detail/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.sale_by_branch_detail`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.sale_by_branch_detail`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

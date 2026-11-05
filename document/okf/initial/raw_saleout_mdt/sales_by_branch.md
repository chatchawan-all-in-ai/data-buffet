---
type: BigQuery Table
title: "sales_by_branch"
description: "One row = one Boonthavorn branch for one report date, a record of source table `sales_by_branch` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=sales_by_branch&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: sales_by_branch
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/bt/sales_by_branch/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `sales_by_branch` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Boonthavorn (BT) sales summary of the company products per branch: month-to-date and year-to-date amount, quantity and square metres against last year.

Read by: [validated_saleout_mdt.sales_by_branch](/validated/validated_saleout_mdt/sales_by_branch.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `VENDOR_ID` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `VENDOR_NAME` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `BRANCH` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `MTD_LAST_YEAR` | FLOAT64 | Month-to-date sales amount for the same period last year (THB). |
| `MTD_CURRENT_YEAR` | FLOAT64 | Month-to-date sales amount this year (THB). |
| `MTD__Growth` | STRING | Month-to-date sales growth versus last year, as percentage text (e.g. `-4.8%`). |
| `YTD_LAST_YEAR` | FLOAT64 | Year-to-date sales amount for the same period last year (THB). |
| `YTD_CURRENT_YEAR` | FLOAT64 | Year-to-date sales amount this year (THB). |
| `YTD__Growth` | STRING | Year-to-date sales growth versus last year, as percentage text (e.g. `67.51%`). |
| `MTD_LAST_YEAR_QTY` | INT64 | Month-to-date sales quantity for the same period last year. |
| `MTD_CURR_YEAR_QTY` | INT64 | Month-to-date sales quantity this year. |
| `MTD_PCT_GROWTH_QTY` | INT64 | Month-to-date sales quantity growth versus last year, in percent. |
| `YTD_LAST_YEAR_QTY` | FLOAT64 | Year-to-date sales quantity for the same period last year. |
| `YTD_CURR_YEAR_QTY` | FLOAT64 | Year-to-date sales quantity this year. |
| `YTD_PCT_GROWTH_QTY` | FLOAT64 | Year-to-date sales quantity growth versus last year, in percent. |
| `MTD_LAST_YEAR_SQM` | INT64 | Month-to-date sales in square metres for the same period last year. |
| `MTD_CURR_YEAR_SQM` | INT64 | Month-to-date sales in square metres this year. |
| `MTD_PCT_GROWTH_SQM` | INT64 | Month-to-date square-metre sales growth versus last year, in percent. |
| `YTD_LAST_YEAR_SQM` | FLOAT64 | Year-to-date sales in square metres for the same period last year. |
| `YTD_CURR_YEAR_SQM` | FLOAT64 | Year-to-date sales in square metres this year. |
| `YTD_PCT_GROWTH_SQM` | FLOAT64 | Year-to-date square-metre sales growth versus last year, in percent. |
| `START_DATE` | STRING | First day of the reporting period. |
| `END_DATE` | STRING | Last day covered by the report (figures are counted up to this date). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/bt/sales_by_branch/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.sales_by_branch`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.sales_by_branch`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "report_sale_subscription"
description: "One row = one SKU at one Thai Watsadu branch in one daily file, a record of source table `report_sale_subscription` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=report_sale_subscription&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: report_sale_subscription
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/tw/reportsalesubscription/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `report_sale_subscription` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Daily Thai Watsadu (TW) sales-and-stock report for the company products: sales on the last sold date, stock on hand and on order per branch and SKU.

Read by: [validated_saleout_mdt.report_sale_subscription](/validated/validated_saleout_mdt/report_sale_subscription.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer, and the validated table does not define one.

# Schema

| Column | Type | Description |
|---|---|---|
| `Store` | STRING | Thai Watsadu branch as code plus name (e.g. `60001-CRC Thai Watsadu ...`), used as the branch code. |
| `Cat` | STRING | Thai Watsadu category code (e.g. `002`). |
| `Sub_Cat` | STRING | Thai Watsadu sub-category code (e.g. `004`). |
| `Brand` | STRING | Product brand. |
| `SKU` | STRING | Thai Watsadu SKU (zero-padded). |
| `Barcode` | STRING | Product barcode (EAN-13). |
| `Description` | STRING | Product description (name). |
| `Product_Type` | STRING | Stock location type of the row (e.g. `Branch`). |
| `Sales_Amount` | FLOAT64 | Sales amount of the SKU at the branch (THB). |
| `Sales_Qty` | INT64 | Sales quantity of the SKU at the branch. |
| `Stock_On_Hand` | FLOAT64 | Stock quantity on hand at the branch. |
| `Stock_On_Order` | INT64 | Stock quantity on open purchase orders. |
| `Last_Sold_Date` | STRING | Date the SKU was last sold at the branch. |
| `Last_Receive_Date` | STRING | Date the SKU was last received at the branch. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/tw/reportsalesubscription/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.report_sale_subscription`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.report_sale_subscription`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

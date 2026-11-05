---
type: BigQuery Table
title: "turnover_brand"
description: "One row = one merchandise category, brand and stock class on one snapshot date, a record of source table `turnover_brand` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=turnover_brand&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: turnover_brand
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/bt/turnover_brand/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `turnover_brand` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Stock turnover by brand and stock class from Boonthavorn (BT) for the company products.

Read by: [validated_saleout_mdt.turnover_brand](/validated/validated_saleout_mdt/turnover_brand.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `VENDOR_ID` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `VENDOR_NAME` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `MCH3` | STRING | Boonthavorn merchandise category, top level (department). |
| `BRAND` | STRING | Product brand. |
| `CLASS_STOCK` | STRING | Boonthavorn stock class (`B3G Class A`, `B3G Class B`, `B3G Class C`, `B3G New`, `B3G Dead`). |
| `UR_COST_AMT` | FLOAT64 | Value of the unrestricted stock at cost for the category, brand and stock class. |
| `T_O` | FLOAT64 | Stock turnover (T/O) of the category, brand and stock class, in days. |
| `START_DATE` | STRING | Stock snapshot date (same as `end_date`). |
| `END_DATE` | STRING | Stock snapshot date. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/bt/turnover_brand/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.turnover_brand`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.turnover_brand`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

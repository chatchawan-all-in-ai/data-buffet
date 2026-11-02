---
type: BigQuery Table
title: "saleout_hp"
description: "One row = one article, branch and sale date, a record of source table `saleout_hp` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_saleout_mdt&t=saleout_hp&page=table"
project_id: databuffet-nonprd
dataset_id: raw_saleout_mdt
table_id: saleout_hp
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

External table over AVRO files in `gs://file-raw-data/saleout_mdt/hp/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `saleout_hp` table from SALEOUT_MDT; nothing is cleaned or deduplicated here. Table meaning: Daily sell-out of the company products at HomePro and MegaHome branches (quantity and amount per article, branch and day). Used by: [validated_saleout_mdt.saleout_hp](/validated/validated_saleout_mdt/saleout_hp.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `CRDATE` | STRING | Date-time HomePro created the report file (`DD/MM/YYYY HH:MM`). |
| `PERIODTYPE` | STRING | Report period type (`D` = daily, `M` = monthly). |
| `PERIODDATE` | STRING | Sale date (`DD/MM/YYYY`). |
| `VENDORNO` | STRING | HomePro vendor number of the supplier (the company). |
| `VENDORNAME` | STRING | Supplier (vendor) name as registered at HomePro. |
| `SITENO` | STRING | HomePro/MegaHome branch code (`S...` = HomePro, `M...` = MegaHome). |
| `SITENAME` | STRING | Branch name. |
| `ITEMNO` | STRING | Item sequence number of the article line in the report. |
| `MCH3` | STRING | HomePro merchandise category code (e.g. `PB` = plumbing, `DW` = door and window). |
| `MCH2DESC` | STRING | HomePro merchandise category, second level, description. |
| `MCH1DESC` | STRING | HomePro merchandise category, lowest level, description. |
| `ARTNO` | STRING | HomePro article (product) number. |
| `ARTDESC` | STRING | HomePro article description (product name). |
| `ARTEAN` | STRING | HomePro in-store EAN barcode (starts with `24`), not a product barcode. |
| `VDARTNO` | STRING | Vendor article number: the GS1 barcode (starts with `885`) used to match `dim_product_master.Barcode`. |
| `VDARTDESC` | STRING | Vendor article description as registered at HomePro. |
| `QTY` | INT64 | Sales quantity (negative = return). |
| `VALUE` | FLOAT64 | Sales amount (THB; negative = return). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_saleout_mdt` (`definitions/initial/saleout_mdt/create_all_table_raw_saleout_mdt.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/saleout_mdt/hp/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_saleout_mdt.saleout_hp`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_saleout_mdt.saleout_hp`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

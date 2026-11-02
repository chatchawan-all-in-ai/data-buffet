---
type: BigQuery Table
title: "tdelivery"
description: "One row = one delivery confirmation of a document on a trip, a record of source table `tdelivery` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tdelivery&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tdelivery
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_gps/tdelivery/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tdelivery` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Delivery confirmations of MAC5 delivery documents on trips, with GPS position, place name and zone. Used by: [validated_mac5.tdelivery](/validated/validated_mac5/tdelivery.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `frun` | STRING | Delivery record identifier. |
| `fmaster` | STRING | Trip identifier (`ttrip.frun`). |
| `fserial_no` | STRING | MAC5 delivery document number confirmed as delivered (matches `mil.milvnos`). |
| `fdatetime` | STRING | Date and time of the delivery confirmation (`yyyyMMddHHmmss`). |
| `flattitude` | STRING | Latitude of the delivery point. |
| `flongtitude` | STRING | Longitude of the delivery point. |
| `fpoi` | STRING | Place name of the delivery point from reverse geocoding. |
| `fzone` | STRING | Delivery zone name (e.g. `ZONE สีส้ม`). |
| `fvat` | STRING | VAT flag of the delivery. |
| `freceive` | STRING | Received flag of the delivery. |
| `fdocument` | STRING | Document number of the delivery. |
| `flatd` | STRING | Latitude of the delivery point as digits without the decimal point. |
| `flongd` | STRING | Longitude of the delivery point as digits without the decimal point. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_gps/tdelivery/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tdelivery`
LIMIT 100
```

---
type: BigQuery Table
title: "tempgpsweb"
description: "One row = one delivered item on one delivery document, a record of source table `tempgpsweb` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tempgpsweb&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tempgpsweb
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tempgpsweb/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tempgpsweb` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Delivery tracking rows from the GPS web app: document, vehicle, item, quantity and loading/release/receipt status. Used by: [validated_mac5.tempgpsweb](/validated/validated_mac5/tempgpsweb.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `fdocument` | STRING | Document number of the delivery (e.g. invoice number). |
| `fserial_no` | STRING | Serial or reference document number of the delivery. |
| `fcode` | STRING | Delivery job code. |
| `fvehicle` | STRING | Registration plate of the delivery vehicle. |
| `fitem` | STRING | Product code or barcode of the delivered item. |
| `fitem2` | STRING | Alternate product code or barcode of the delivered item. |
| `qty2` | INT64 | Quantity of the item delivered. |
| `s1` | STRING | Loading status text in Thai (goods loaded onto the truck). |
| `s2` | STRING | Truck release status text in Thai (truck released or not released). |
| `s3` | STRING | Receipt status text in Thai (goods received or not yet delivered). |
| `stt` | STRING | Status code of the delivery row (1, 2). |
| `username` | STRING | User code of the person who recorded the row. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tempgpsweb/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tempgpsweb`
LIMIT 100
```

---
type: BigQuery Table
title: "ttrip_document"
description: "One row = one scanned item unit loaded on a delivery trip, a record of source table `ttrip_document` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=ttrip_document&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: ttrip_document
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_gps/ttrip_document/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `ttrip_document` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Item scans of delivery documents loaded on trips, linking each scanned unit to its trip and MAC5 delivery document; source of dim_delivery and fact_delivery.

Read by: [validated_mac5.ttrip_document](/validated/validated_mac5/ttrip_document.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `frun` | STRING | Scan record identifier (timestamp `yyMMddHHmmss` plus sequence). |
| `fmaster` | STRING | Trip identifier (`ttrip.frun`). |
| `fdocument` | STRING | MAC5 delivery document number loaded on the trip (matches `mil.milvnos` of type IS). |
| `fserial_no` | STRING | Scanned serial or barcode of the unit. |
| `fitem` | STRING | Stock code of the scanned item. |
| `fusername` | STRING | Code of the user who scanned the item. |
| `fdatetime` | STRING | Date and time the item was scanned (`yyyyMMddHHmmss`). |
| `fitem2` | STRING | Alternative stock code of the scanned item, used when `fitem` does not match the invoice line. |
| `fdoc_type` | STRING | Document type of `fdocument` (e.g. `IS`). |
| `fcancel` | STRING | Customer refusal flag (0 = received, other = refused). |
| `fref1` | STRING | Sales order number referenced by the delivery document. |
| `fdocument_rt` | INT64 | Document returned flag. |
| `fdocument_rtdate` | STRING | Date the document was returned. |
| `fdocument_ac` | INT64 | Document received by accounting flag. |
| `fdocument_acdate` | STRING | Date the document was received by accounting. |
| `frepro` | STRING | Reprocess reference of the scan. |
| `fqty_order` | INT64 | Ordered quantity of the item on the document. |
| `fitemdoc` | STRING | Item reference of the document line. |
| `fitem3` | STRING | Third stock code or barcode of the scanned item. |
| `fprice` | FLOAT64 | Price value of the scanned item. |
| `fin365` | INT64 | IN365 flag of the scan. |
| `im_mac` | STRING | Device (MAC) identifier of the scanner. |
| `post` | STRING | Posting flag of the scan. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_gps/ttrip_document/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.ttrip_document`
LIMIT 100
```

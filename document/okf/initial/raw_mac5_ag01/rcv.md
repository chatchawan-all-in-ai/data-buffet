---
type: BigQuery Table
title: "rcv"
description: "One row = one received serial-numbered unit, a record of source table `rcv` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=rcv&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: rcv
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/rcv/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `rcv` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Finished-goods receiving log by unit serial number (product, warehouse, order and packing details). Used by: [validated_mac5.rcv](/validated/validated_mac5/rcv.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `serial` | STRING | Serial number of the received unit; unique within the company. |
| `rcvdate` | STRING | Receiving date, as text. |
| `rcvtype` | INT64 | Receiving type code. |
| `rcvvnos` | STRING | Number of the receiving document. |
| `rcvstk` | STRING | Product (stock) code of the received unit. |
| `descT1` | STRING | Product description in Thai. |
| `qty` | STRING | Received quantity, as text. |
| `unit` | STRING | Unit of the received quantity. |
| `rcvsto` | STRING | Warehouse (store) code the unit is received into. |
| `username` | STRING | User who recorded the receipt. |
| `remark` | STRING | Free-text remark. |
| `rcvtime` | STRING | Receiving time, as text. |
| `Fdatetime2` | STRING | Record date and time, as text. |
| `rcvStatus` | STRING | Receiving status code. |
| `rcvtypeFG` | STRING | Finished-goods receiving type code. |
| `rcvstatusMR` | STRING | Material-receipt status code. |
| `rcvzone` | STRING | Storage zone code. |
| `rcvOrder` | STRING | Order number the unit is received for. |
| `rcvCommand` | STRING | Production command (work order) number. |
| `rcvExtCode` | STRING | External code of the received unit. |
| `mixVnos` | STRING | Number of the linked ERP document. |
| `mixDate` | STRING | Date of the linked ERP document. |
| `rcvTranCode` | STRING | Transfer code of the receipt. |
| `rcvCancel` | INT64 | Cancellation flag of the receipt. |
| `rcvOrder_Pack` | STRING | Order number used for packing. |
| `adjVnos` | STRING | Number of the related stock-adjustment document. |
| `PackDate` | STRING | Packing date, as text. |
| `PackTime` | STRING | Packing time, as text. |
| `rcvConvert` | INT64 | Flag: receipt converted into an ERP document. |
| `Odate` | STRING | Date of the last status change, as text. |
| `Ouser` | STRING | User of the last status change. |
| `FMIL2LISTNO` | INT64 | Line number of the linked document line. |
| `Ostatus` | STRING | Status after the last change. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/rcv/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.rcv`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.rcv`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

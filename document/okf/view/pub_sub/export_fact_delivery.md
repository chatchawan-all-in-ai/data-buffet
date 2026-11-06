---
type: BigQuery View
title: "export_fact_delivery"
description: "One row = one delivery item of a delivery document, exposed for the Pub/Sub export of fact_table.fact_delivery with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_fact_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_fact_delivery
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_fact_delivery.sqlx"
    title: "Dataform definition (view/pub_sub/export_fact_delivery.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:47:32+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [fact_table.fact_delivery](/fact/fact_delivery.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-fact_delivery`.

# Grain and key

One row = one delivery item of a delivery document: key `companyID`, `documentID`, `item`, `occurrence` (unique); `row_key` is the JSON of that key. `occurrence` is computed as the position of the row among source rows with the same business key, ordered by their data JSON; it appears only inside `row_key`. `companyID`, `documentID`, `item` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactTransDeliverySK` | INT64 | [fact_transaction_delivery](/fact/fact_transaction_delivery.md).FactTransDeliverySK of the invoice line (join documentID = milvnos, case-insensitive item); NULL if unmatched. |
| `milCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `DeliveryDate` | DATE | Date part (first 8 digits yyyymmdd) of `ttrip_document.fdatetime`. |
| `Vehicle` | STRING | Vehicle identifier of the trip (`ttrip.fvehicle`). |
| `Zone` | STRING | Delivery zone from `tdelivery.fzone`. |
| `Point` | STRING | Delivery point-of-interest from `tdelivery.fpoi`. |
| `documentStatus_2` | INT64 | Count of records not yet loaded ('ยังไม่จัดของ'). |
| `deliveryStatus_2` | INT64 | Count of records whose vehicle was not released ('ไม่ปล่อยรถ'). |
| `shipmentStatus_2` | INT64 | Count of records received by the customer ('รับสินค้าแล้ว': delivered and `fcancel = '0'`). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_fact_delivery.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [fact_table.fact_delivery](/fact/fact_delivery.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_fact_delivery`
GROUP BY row_key
HAVING n > 1
```

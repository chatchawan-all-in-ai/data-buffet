---
type: BigQuery Table
title: "order_from_allkon_m"
description: "One row = one order received from the Allkons platform, a record of source table `order_from_allkon_m` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=order_from_allkon_m&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: order_from_allkon_m
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/order_from_allkon_m/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `order_from_allkon_m` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Orders received from the Allkons platform, with promotion type, source and processing statuses. Used by: [validated_mac5.order_from_allkon_m](/validated/validated_mac5/order_from_allkon_m.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Row identifier of the order. |
| `order_no` | STRING | Allkons platform order number (e.g. `QOAG-00158-00048-22-09`). |
| `status` | STRING | Status code of the order row (1, 2, 3). |
| `create_date` | STRING | Date and time the order was received. |
| `promotion_type` | STRING | Promotion types applied to the order (e.g. `Premium`, `ComboSet`, `VolumePrice`, comma-separated). |
| `notes` | STRING | Processing notes of the order import, such as confirm status codes or `#order_null`. |
| `sub_order` | STRING | Sub-order number of the order. |
| `made_from` | STRING | Source application that created the order (e.g. `AKM`, `AMRP`). |
| `datetime` | STRING | Date and time of the order event. |
| `deliverystatus` | STRING | Delivery status code of the order. |
| `cancelstatus` | STRING | Cancel status code of the order (0, 1, 2). |
| `confirmstatus` | STRING | Confirm status code of the order (0, 1, 2). |
| `order_source` | STRING | Channel the order came from (e.g. `AK Platform`, `BOT (Semi-Auto)`). |
| `is_complete` | INT64 | Completion status code of the order import (0 to 3). |
| `update_date` | STRING | Date and time the order row was last updated. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/order_from_allkon_m/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.order_from_allkon_m`
LIMIT 100
```

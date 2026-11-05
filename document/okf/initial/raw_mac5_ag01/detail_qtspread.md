---
type: BigQuery Table
title: "detail_qtspread"
description: "One row = one item line of a quotation spread, a record of source table `detail_qtspread` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=detail_qtspread&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: detail_qtspread
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/detail_qtspread/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `detail_qtspread` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Item lines of quotation spreads: stock code and quantity taken from a quotation detail line into one order. Used by: [validated_mac5.detail_qtspread](/validated/validated_mac5/detail_qtspread.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Row identifier of the spread line. |
| `ref_id` | INT64 | Quotation spread identifier (`main_qtspread.id`). |
| `qtid` | INT64 | Quotation identifier (`tbook_quotation.id`). |
| `quodeid` | STRING | Quotation detail line identifier (`tbook_quodetail.id`). |
| `stkcode` | STRING | MAC5 stock code of the item. |
| `quantity` | FLOAT64 | Quantity of the item spread into this order. |
| `price` | FLOAT64 | Unit price of the item. |
| `total` | STRING | Line total of the item. |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dinsert` | STRING | Date and time the row was created. |
| `dupdate` | STRING | Date and time the row was last updated. |
| `status` | STRING | Status code of the spread line (1 = active, 3 = cancelled). |
| `link` | STRING | Link reference of the spread line. |
| `type` | STRING | Line type of the spread line. |
| `fandex` | STRING | FANDEX reference of the spread line. |
| `itemsize` | STRING | Item size of the spread line. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/detail_qtspread/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.detail_qtspread`
LIMIT 100
```

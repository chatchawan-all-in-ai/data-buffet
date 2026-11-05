---
type: BigQuery Table
title: "qt_spread_to_mih"
description: "One row = one link from a quotation spread to a pre-order, a record of source table `qt_spread_to_mih` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=qt_spread_to_mih&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: qt_spread_to_mih
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/qt_spread_to_mih/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `qt_spread_to_mih` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Links from quotation spreads (main_qtspread) to the pre-order numbers created from them. Used by: [validated_mac5.qt_spread_to_mih](/validated/validated_mac5/qt_spread_to_mih.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Row identifier of the link. |
| `qt_spread_ref_id` | INT64 | Quotation spread identifier (`main_qtspread.id`). |
| `qtid` | STRING | Quotation identifier (`tbook_quotation.id`). |
| `mihvnos` | STRING | Document number, unique within company and document type. |
| `status` | INT64 | Status flag of the link (1 = active). |
| `rdysendtomac5` | INT64 | Ready-to-send-to-MAC5 flag. |
| `sto` | STRING | Stock location code of the order. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/qt_spread_to_mih/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.qt_spread_to_mih`
LIMIT 100
```

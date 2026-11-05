---
type: BigQuery Table
title: "tbook_givestk"
description: "One row = one giveaway item line of a quotation spread, a record of source table `tbook_givestk` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbook_givestk&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbook_givestk
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbook_givestk/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbook_givestk` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Giveaway items earned by sold items in quotation spreads, with the sold and giveaway stock codes and quantity. Used by: [validated_mac5.tbook_givestk](/validated/validated_mac5/tbook_givestk.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Row identifier of the giveaway line. |
| `qtid` | INT64 | Quotation identifier (`tbook_quotation.id`). |
| `qtspread_ref_id` | INT64 | Sequence number of the quotation spread (`main_qtspread.ref_id` within the same quotation). |
| `quodeid` | INT64 | Quotation detail line of the giveaway item (`tbook_quodetail.id`). |
| `quolinkdel` | INT64 | Quotation detail line of the sold item that earns the giveaway (`tbook_quodetail.id`). |
| `stkcode` | STRING | Stock code of the sold item that earns the giveaway. |
| `stkgive` | STRING | Stock code of the giveaway item. |
| `quantity` | INT64 | Quantity of the giveaway item. |
| `datetimekey` | STRING | Date and time the giveaway line was keyed. |
| `status` | INT64 | Status code of the giveaway line (1, 3). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbook_givestk/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbook_givestk`
LIMIT 100
```

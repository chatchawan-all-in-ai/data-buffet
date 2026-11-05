---
type: BigQuery Table
title: "pathfilestamper"
description: "One row = one file attached to an order, a record of source table `pathfilestamper` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=pathfilestamper&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: pathfilestamper
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/pathfilestamper/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `pathfilestamper` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Files attached to quotation-app orders (POs, pay-in slips, maps, delivery proofs), with file share paths and payment notes.

Read by: [validated_mac5.pathfilestamper](/validated/validated_mac5/pathfilestamper.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Row identifier of the file record. |
| `mainqtid` | INT64 | Quotation spread identifier (`main_qtspread.id`). |
| `preorderno` | STRING | Pre-order number from the quotation app (T-prefixed). |
| `orderno` | STRING | MAC5 sales order number the file belongs to. |
| `type` | STRING | File type (`PO`, `Payin`, `Map`, `Delivery`, `MEMO`, `BOQ`, `Other`). |
| `path212` | STRING | Path of the file on the web upload server. |
| `path10acc` | STRING | Path of the file on the accounting file share. |
| `path10fac` | STRING | Path of the file on the factory admin file share. |
| `filename` | STRING | File name (e.g. `<order>-PAYIN.pdf`). |
| `uinsert` | STRING | Employee code of the user who uploaded the file, or `bot`. |
| `date` | STRING | Date and time the file was uploaded (text). |
| `status` | INT64 | Active flag (1 = active). |
| `pathqtid` | STRING | Identifier of the quotation-app record the file was uploaded under. |
| `note` | STRING | Payment note of the file (e.g. 100 percent transfer, 30 percent deposit). |
| `datepayinadmin` | STRING | Date the pay-in was confirmed by the admin. |
| `refpo` | STRING | Customer purchase order reference. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/pathfilestamper/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.pathfilestamper`
LIMIT 100
```

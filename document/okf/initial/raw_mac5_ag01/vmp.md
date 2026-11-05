---
type: BigQuery Table
title: "vmp"
description: "One row = one month of document counts, a record of source table `vmp` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=vmp&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: vmp
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/vmp/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `vmp` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Monthly counts of documents per module (GL books, AR, AP, inventory, payroll).

Read by: [validated_mac5.vmp](/validated/validated_mac5/vmp.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `VMmonth` | INT64 | Month (1 to 12) the counts refer to. |
| `VMyear` | INT64 | Year (AD) the counts refer to. |
| `VMGLtotal` | INT64 | Total number of GL vouchers in the month. |
| `VMGLb1` | INT64 | Number of GL vouchers in GL book 1 in the month. |
| `VMGLb2` | INT64 | Number of GL vouchers in GL book 2 in the month. |
| `VMGLb3` | INT64 | Number of GL vouchers in GL book 3 in the month. |
| `VMGLb4` | INT64 | Number of GL vouchers in GL book 4 in the month. |
| `VMGLb5` | INT64 | Number of GL vouchers in GL book 5 in the month. |
| `VMGLb6` | INT64 | Number of GL vouchers in GL book 6 in the month. |
| `VMGLb7` | INT64 | Number of GL vouchers in GL book 7 in the month. |
| `VMGLb8` | INT64 | Number of GL vouchers in GL book 8 in the month. |
| `VMGLb9` | INT64 | Number of GL vouchers in GL book 9 in the month. |
| `VMGLb10` | INT64 | Number of GL vouchers in GL book 10 in the month. |
| `VMGLb11` | INT64 | Number of GL vouchers in GL book 11 in the month. |
| `VMGLb12` | INT64 | Number of GL vouchers in GL book 12 in the month. |
| `VMGLb13` | INT64 | Number of GL vouchers in GL book 13 in the month. |
| `VMGLb14` | INT64 | Number of GL vouchers in GL book 14 in the month. |
| `VMGLb15` | INT64 | Number of GL vouchers in GL book 15 in the month. |
| `VMGLb16` | INT64 | Number of GL vouchers in GL book 16 in the month. |
| `VMGLb17` | INT64 | Number of GL vouchers in GL book 17 in the month. |
| `VMGLb18` | INT64 | Number of GL vouchers in GL book 18 in the month. |
| `VMGLb19` | INT64 | Number of GL vouchers in GL book 19 in the month. |
| `VMGLb20` | INT64 | Number of GL vouchers in GL book 20 in the month. |
| `VMGLb21` | INT64 | Number of GL vouchers in GL book 21 in the month. |
| `VMGLb22` | INT64 | Number of GL vouchers in GL book 22 in the month. |
| `VMGLb23` | INT64 | Number of GL vouchers in GL book 23 in the month. |
| `VMGLb24` | INT64 | Number of GL vouchers in GL book 24 in the month. |
| `VMGLb25` | INT64 | Number of GL vouchers in GL book 25 in the month. |
| `VMGLb26` | INT64 | Number of GL vouchers in GL book 26 in the month. |
| `VMGLb27` | INT64 | Number of GL vouchers in GL book 27 in the month. |
| `VMGLb28` | INT64 | Number of GL vouchers in GL book 28 in the month. |
| `VMGLb29` | INT64 | Number of GL vouchers in GL book 29 in the month. |
| `VMGLb30` | INT64 | Number of GL vouchers in GL book 30 in the month. |
| `VMGLb31` | INT64 | Number of GL vouchers in GL book 31 in the month. |
| `VMGLb32` | INT64 | Number of GL vouchers in GL book 32 in the month. |
| `VMGLb33` | INT64 | Number of GL vouchers in GL book 33 in the month. |
| `VMGLb34` | INT64 | Number of GL vouchers in GL book 34 in the month. |
| `VMGLb35` | INT64 | Number of GL vouchers in GL book 35 in the month. |
| `VMGLb36` | INT64 | Number of GL vouchers in GL book 36 in the month. |
| `VMGLb37` | INT64 | Number of GL vouchers in GL book 37 in the month. |
| `VMGLb38` | INT64 | Number of GL vouchers in GL book 38 in the month. |
| `VMGLb39` | INT64 | Number of GL vouchers in GL book 39 in the month. |
| `VMGLb40` | INT64 | Number of GL vouchers in GL book 40 in the month. |
| `VMGLb41` | INT64 | Number of GL vouchers in GL book 41 in the month. |
| `VMGLb42` | INT64 | Number of GL vouchers in GL book 42 in the month. |
| `VMGLb43` | INT64 | Number of GL vouchers in GL book 43 in the month. |
| `VMGLb44` | INT64 | Number of GL vouchers in GL book 44 in the month. |
| `VMGLb45` | INT64 | Number of GL vouchers in GL book 45 in the month. |
| `VMGLb46` | INT64 | Number of GL vouchers in GL book 46 in the month. |
| `VMGLb47` | INT64 | Number of GL vouchers in GL book 47 in the month. |
| `VMGLb48` | INT64 | Number of GL vouchers in GL book 48 in the month. |
| `VMGLb49` | INT64 | Number of GL vouchers in GL book 49 in the month. |
| `VMGLb50` | INT64 | Number of GL vouchers in GL book 50 in the month. |
| `VMARtotal` | INT64 | Total number of AR (sales) documents in the month. |
| `VMARquo` | INT64 | Number of AR quotations in the month. |
| `VMARpo` | INT64 | Number of AR sales orders in the month. |
| `VMARdel` | INT64 | Number of AR delivery notes in the month. |
| `VMARbil` | INT64 | Number of AR billing notes in the month. |
| `VMARinv` | INT64 | Number of AR invoices in the month. |
| `VMARdrn` | INT64 | Number of AR debit notes in the month. |
| `VMARcrn` | INT64 | Number of AR credit notes in the month. |
| `VMARcash` | INT64 | Number of AR cash sales in the month. |
| `VMARlease` | INT64 | Number of AR hire-purchase documents in the month. |
| `VMARrec` | INT64 | Number of AR receipts in the month. |
| `VMAPtotal` | INT64 | Total number of AP (purchase) documents in the month. |
| `VMAPquo` | INT64 | Number of AP supplier quotations in the month. |
| `VMAPpo` | INT64 | Number of AP purchase orders in the month. |
| `VMAPdel` | INT64 | Number of AP goods received notes in the month. |
| `VMAPbil` | INT64 | Number of AP supplier billing notes in the month. |
| `VMAPinv` | INT64 | Number of AP supplier invoices in the month. |
| `VMAPdrn` | INT64 | Number of AP debit notes in the month. |
| `VMAPcrn` | INT64 | Number of AP credit notes in the month. |
| `VMAPcash` | INT64 | Number of AP cash purchases in the month. |
| `VMAPlease` | INT64 | Number of AP hire-purchase documents in the month. |
| `VMAPrec` | INT64 | Number of AP payment vouchers in the month. |
| `VMICtotal` | INT64 | Total number of inventory documents in the month. |
| `VMICgin` | INT64 | Number of inventory goods receipts in the month. |
| `VMICgout` | INT64 | Number of inventory goods issues in the month. |
| `VMICgrt` | INT64 | Number of inventory goods returns in the month. |
| `VMICgrf` | INT64 | Number of inventory goods refunds in the month. |
| `VMICjour` | INT64 | Number of inventory stock journal entries in the month. |
| `VMICmstr` | INT64 | Number of inventory stock transfers in the month. |
| `VMICpr` | INT64 | Number of inventory production documents in the month. |
| `VMPRtotal` | INT64 | Total number of payroll documents in the month. |
| `VMPRsalary` | INT64 | Number of payroll salary documents in the month. |
| `VMPRmemo` | INT64 | Number of payroll memo documents in the month. |
| `rowguid` | STRING | Row GUID that uniquely identifies the record in the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/vmp/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.vmp`
LIMIT 100
```

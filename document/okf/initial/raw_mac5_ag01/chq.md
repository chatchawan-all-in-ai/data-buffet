---
type: BigQuery Table
title: "chq"
description: "One row = one cheque, a record of source table `chq` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=chq&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: chq
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/chq/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `chq` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Cheques received from customers and issued to suppliers, with bank, dates, amount, status and memo-derived payment splits. Used by: [validated_mac5.chq](/validated/validated_mac5/chq.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `chqno` | STRING | Cheque number. |
| `chqbank` | STRING | Bank code of the cheque (e.g. `BBL`, `KBANK`, `SCB`). |
| `chqacode` | STRING | General-ledger account code of the cheque; sampled MAC5 records show 112001 for received cheques and 211101, 212000, 212400, and 214201 for issued cheques. |
| `chqcus` | STRING | Customer code (supplier code for issued cheques), matching `deb.debcode`. |
| `chqdatec` | STRING | Date written on the cheque. |
| `chqdater` | STRING | Date the cheque was received or issued. |
| `chqdatep` | STRING | Date the cheque was passed (cleared) at the bank. |
| `chqtype` | INT64 | Cheque direction (1 = received from customer, 2 = issued to supplier). |
| `chqstatus` | INT64 | Cheque status (1 = cleared, 2 = bounced, 3 = due). |
| `chqtotal` | FLOAT64 | Cheque amount. |
| `chqmemo` | STRING | Full cheque memo as entered, including transfer and payment-split notes. |
| `chqgl` | INT64 | Flag: cheque posted to the general ledger (1 = posted). |
| `chqmi` | INT64 | Cheque handling mode code (0, 1, 2). |
| `chqown` | INT64 | Cheque ownership code (1 = own cheque, 2 = third-party cheque). |
| `chqtag` | INT64 | Tag marker of the cheque. |
| `chqstatusn` | INT64 | Cheque posting status (1 = POST, 2 = PASS, 3 = cleared, 4 = not cleared, 5 = adjusted, 6 = voucher cancelled). |
| `chqlock` | INT64 | Flag: cheque locked against editing. |
| `chqpassgl` | INT64 | Flag: cheque clearing posted to the general ledger (-1 = posted). |
| `chqjob` | STRING | Job code of the cheque (sales job or project category). |
| `chqdep` | STRING | Department code of the cheque, used as the sales channel code. |
| `chqper` | STRING | Salesperson (employee) code of the cheque. |
| `chqzon` | STRING | Zone code of the cheque. |
| `chqrcode` | STRING | General-ledger account code of the bank account the cheque is deposited to or paid from. |
| `chqeditlk` | STRING | Timestamp of the current edit lock on the cheque. |
| `chqkeyuser` | STRING | User code of the person who keyed the cheque. |
| `chqkeydate` | STRING | Date and time the cheque was keyed. |
| `chqdeduct` | FLOAT64 | Amount deducted from the cheque, such as bank fees. |
| `chqecode` | STRING | External code of the cheque. |
| `chqbranch` | STRING | Bank branch of the cheque. |
| `chqmec` | STRING | Memo-card code of the cheque, matching `mec.meccode`. |
| `chqdatev` | STRING | Voucher date of the cheque. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/chq/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.chq`
LIMIT 100
```

---
type: BigQuery Table
title: "mec"
description: "One row = one memo card, a record of source table `mec` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mec&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: mec
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mec/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `mec` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Memo cards attached to documents (address, contact and shop or branch name per template), referenced by `mihmec`/`milmec`. Used by: [validated_mac5.mec](/validated/validated_mac5/mec.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `MECcode` | STRING | Memo-card code, referenced by `mihmec` and `milmec` on documents. |
| `MECtpl` | INT64 | Template number that defines the layout of the card's text fields. |
| `MECtoCType` | INT64 | Owner type of the card (2 = card attached to a customer through `mectocode`, 11 = general card, 8 = other). |
| `MECtoCode` | STRING | Code of the record the card belongs to, such as the customer code when `mectoctype` is 2. |
| `MECt1` | STRING | Text field 1 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt2` | STRING | Text field 2 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt3` | STRING | Text field 3 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt4` | STRING | Text field 4 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt5` | STRING | Text field 5 of the card (an address part, contact name or postal code, depending on the template). |
| `MECd1` | STRING | Date field 1 of the card. |
| `MECd2` | STRING | Date field 2 of the card. |
| `MECd3` | STRING | Date field 3 of the card. |
| `MECi1` | INT64 | Integer field 1 of the card. |
| `MECi2` | INT64 | Integer field 2 of the card. |
| `MECc1` | FLOAT64 | Numeric field 1 of the card. |
| `MECc2` | FLOAT64 | Numeric field 2 of the card. |
| `MECc3` | FLOAT64 | Numeric field 3 of the card. |
| `MECc4` | FLOAT64 | Numeric field 4 of the card. |
| `MECc5` | FLOAT64 | Numeric field 5 of the card. |
| `MECm1` | STRING | Memo field 1 of the card. |
| `MECm2` | STRING | Memo field 2 of the card. |
| `MECm3` | STRING | Memo field 3 of the card. |
| `MECm4` | STRING | Memo field 4 of the card. |
| `MECm5` | STRING | Memo field 5 of the card. |
| `MECm6` | STRING | Memo field 6 of the card. |
| `MECm7` | STRING | Memo field 7 of the card. |
| `MECm8` | STRING | Memo field 8 of the card. |
| `MECm9` | STRING | Memo field 9 of the card. |
| `MECdesc` | STRING | Card title, used as the shop or branch name of chain-store customers in invoice reporting. |
| `MEChide` | INT64 | Flag: card hidden from selection lists. |
| `MEClock` | INT64 | Flag: card locked against editing. |
| `MECeditLK` | STRING | Timestamp of the current edit lock on the card. |
| `MECrefWE` | STRING | Web reference of the card. |
| `MECsortN` | STRING | Sort name of the card. |
| `MECt6` | STRING | Text field 6 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt7` | STRING | Text field 7 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt8` | STRING | Text field 8 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt9` | STRING | Text field 9 of the card (an address part, contact name or postal code, depending on the template). |
| `MECt10` | STRING | Text field 10 of the card (an address part, contact name or postal code, depending on the template). |
| `MECeditDT` | STRING | Date and time the card was last edited. |
| `MECeditMF` | STRING | User code of the person who last edited the card. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mec/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mec`
LIMIT 100
```

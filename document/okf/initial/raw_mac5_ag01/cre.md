---
type: BigQuery Table
title: "cre"
description: "One row = one supplier, a record of source table `cre` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cre&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: cre
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cre/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `cre` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Supplier (creditor) master of MAC5: names, address, tax ID, payable account and terms. Used by: [validated_mac5.cre](/validated/validated_mac5/cre.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `crecode` | STRING | Supplier (creditor) code. |
| `cregroup` | STRING | Supplier group code. |
| `crenamet` | STRING | Supplier name in Thai. |
| `crenamee` | STRING | Supplier name in English. |
| `crecontactt` | STRING | Contact person name in Thai. |
| `crecontacte` | STRING | Contact person name in English. |
| `creadd1at` | STRING | Thai address line 1 (house number, road, sub-district). |
| `creadd2at` | STRING | Thai address line 2 (usually the province). |
| `creadd3at` | STRING | Thai address line 3 (usually the postal code). |
| `creadd1ae` | STRING | English address line 1. |
| `creadd2ae` | STRING | English address line 2. |
| `creadd3ae` | STRING | English address line 3. |
| `cretel` | STRING | Supplier phone number. |
| `cretaxnos` | STRING | Supplier 13-digit tax identification number. |
| `crezone` | STRING | Zone code of the supplier. |
| `cregrade` | STRING | Grade of the supplier. |
| `crelimit` | FLOAT64 | Credit limit granted by the supplier. |
| `cretaxclass` | FLOAT64 | Withholding tax class or rate of the supplier. |
| `cregoodsdef` | INT64 | Default goods type of the supplier. |
| `crecreditterm` | INT64 | Credit term in days granted by the supplier. |
| `credate` | STRING | Date the supplier record was opened. |
| `crehide` | INT64 | Flag: supplier hidden from selection lists. |
| `crefax` | STRING | Supplier fax number. |
| `creemail` | STRING | Supplier email address. |
| `cretarget` | FLOAT64 | Purchase target for the supplier. |
| `crememo` | STRING | Free-text memo of the supplier. |
| `creac` | STRING | General-ledger payable account code of the supplier (e.g. 214401, 214999). |
| `crelock` | INT64 | Flag: supplier record locked against editing. |
| `creoname` | STRING | Other (alternative) name of the supplier. |
| `creprice` | STRING | Price level of the supplier. |
| `creeditlk` | STRING | Timestamp of the current edit lock on the supplier record. |
| `crerefwe` | STRING | Web reference of the supplier. |
| `cresortnt` | STRING | Thai sort name of the supplier. |
| `cresortne` | STRING | English sort name of the supplier. |
| `crecardid` | STRING | 13-digit national ID card number of an individual supplier. |
| `creeditdt` | STRING | Date and time the supplier record was last edited. |
| `creeditmf` | STRING | User code of the person who last edited the supplier record. |
| `cretaxtype` | INT64 | Tax type of the supplier (0 or 1). |
| `creinex` | INT64 | VAT inclusion mode of the supplier's prices. |
| `crebranch` | STRING | Supplier branch number for tax purposes (`00000` = head office). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cre/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cre`
LIMIT 100
```

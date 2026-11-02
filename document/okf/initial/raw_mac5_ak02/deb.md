---
type: BigQuery Table
title: "deb"
description: "One row = one customer (debtor), a record of source table `deb` (MAC5 for company `ak02`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ak02&t=deb&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ak02
table_id: deb
tags: ["initial", "raw_mac5_ak02", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_ak02.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_ak02.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ak02/deb/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `deb` table from MAC5 for company `ak02`; nothing is cleaned or deduplicated here. Table meaning: Customer master of the MAC5 ERP: names, addresses, tax ID, group, grade, salesperson, credit limit and terms. Used by: [validated_mac5.deb](/validated/validated_mac5/deb.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `debcode` | STRING | Customer (debtor) code. |
| `debgroup` | STRING | Customer group code (e.g. HP, TW, BT, GB, MH, DOHOME); drives channel matching in the sale-rep rules. |
| `debchannel` | STRING | Sales channel of the customer. |
| `debtitle` | STRING | Name title of the customer. |
| `debnamet` | STRING | Customer name in Thai. |
| `debnamee` | STRING | Customer name in English. |
| `debaddfull` | STRING | Full address of the customer in one string. |
| `debcontactt` | STRING | Contact person name in Thai. |
| `debcontacte` | STRING | Contact person name in English. |
| `debadd1at` | STRING | Thai address line 1 of the customer. |
| `debadd2at` | STRING | Thai address line 2 of the customer. |
| `debadd3at` | STRING | Thai address line 3 of the customer. |
| `debadd1ae` | STRING | English address line 1 of the customer. |
| `debadd2ae` | STRING | English address line 2 of the customer. |
| `debadd3ae` | STRING | English address line 3 of the customer. |
| `debaddr` | STRING | House number part of the customer address. |
| `debroad` | STRING | Road of the customer address. |
| `debtambol` | STRING | Sub-district (tambon) of the customer address. |
| `debaumphur` | STRING | District (amphoe) of the customer address. |
| `debprov` | STRING | Province of the customer address. |
| `debzipcode` | STRING | Postal code of the customer address. |
| `debtel` | STRING | Phone number(s) of the customer. |
| `debcodenv` | STRING | Customer code of the same customer in the NV company database. |
| `debcodetm` | STRING | Customer code of the same customer in the TM company database. |
| `debcodenano` | STRING | Customer code of the same customer in the NANO company database. |
| `debcodeteem` | STRING | Customer code of the same customer in the TEEM company database. |
| `debcodete` | STRING | Customer code of the same customer in the TE company database. |
| `debcodesw` | STRING | Customer code of the same customer in the SW company database. |
| `debcoderp` | STRING | Customer code of the same customer in the RP company database. |
| `debtaxnos` | STRING | 13-digit tax ID of the customer. |
| `debcitizenid` | STRING | 13-digit citizen ID of an individual customer. |
| `debzone` | STRING | Sales zone code of the customer (e.g. `001`, `D-001`). |
| `debgrade` | STRING | Customer grade code. |
| `deblimit` | FLOAT64 | Credit limit of the customer in baht. |
| `debtaxclass` | FLOAT64 | VAT rate applied to the customer in percent (7 or 0). |
| `debgoodsdef` | FLOAT64 | Default goods discount of the customer. |
| `debcreditterm` | INT64 | Credit term in days. |
| `debpaytype` | INT64 | Payment schedule type code (1, 2). |
| `debpayday` | INT64 | Payment day setting of the payment schedule. |
| `debpayon1` | INT64 | Payment day 1 of the payment schedule. |
| `debpayon2` | INT64 | Payment day 2 of the payment schedule. |
| `debpayon3` | INT64 | Payment day 3 of the payment schedule. |
| `debpayon4` | INT64 | Payment day 4 of the payment schedule. |
| `debpayon5` | INT64 | Payment day 5 of the payment schedule. |
| `debpayn1` | INT64 | Payment schedule parameter 1. |
| `debpayn2` | INT64 | Payment schedule parameter 2. |
| `debbgrtype` | INT64 | Billing schedule type code. |
| `debbgrday` | INT64 | Billing day setting of the billing schedule. |
| `debbgron1` | INT64 | Billing day 1 of the billing schedule. |
| `debbgron2` | INT64 | Billing day 2 of the billing schedule. |
| `debbgron3` | INT64 | Billing day 3 of the billing schedule. |
| `debbgron4` | INT64 | Billing day 4 of the billing schedule. |
| `debbgron5` | INT64 | Billing day 5 of the billing schedule. |
| `debdate` | STRING | Date the customer record was created. |
| `debhide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `debfax` | STRING | Fax number of the customer. |
| `debemail` | STRING | Email address of the customer. |
| `debtarget` | FLOAT64 | Sales target of the customer. |
| `debmemo` | STRING | Free-text memo on the customer. |
| `debac` | STRING | AR GL account code of the customer (e.g. `112200`). |
| `deblock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `deboname` | STRING | Other name of the customer (e.g. branch label). |
| `debcm1` | STRING | Comment field 1 of the customer. |
| `debcm2` | STRING | Comment field 2 of the customer. |
| `debcm3` | STRING | Comment field 3 of the customer. |
| `debcm4` | STRING | Comment field 4 of the customer. |
| `debcm5` | STRING | Comment field 5 of the customer. |
| `debcm6` | STRING | Comment field 6 of the customer. |
| `debcm7` | STRING | Comment field 7 of the customer. |
| `debcm8` | STRING | Comment field 8 of the customer. |
| `debcm9` | STRING | Comment field 9 of the customer. |
| `debcm10` | STRING | Comment field 10 of the customer. |
| `debprice` | STRING | Default price level code of the customer. |
| `debeditlk` | STRING | Date and time the record was locked for editing. |
| `debrefwe` | STRING | External reference code of the record. |
| `debbillad` | INT64 | Billing-address flag of the customer. |
| `debsortnt` | STRING | Thai sort key of the customer (usually the Thai name). |
| `debsortne` | STRING | English sort key of the customer. |
| `debsalesp` | STRING | Salesperson code assigned to the customer (joins `per.percode`). |
| `debeditdt` | STRING | Date and time the record was last edited. |
| `debeditmf` | STRING | User code of the person who last edited the record. |
| `debinex` | INT64 | VAT include/exclude flag of the customer's prices (`1`, `0`). |
| `debbranch` | STRING | Tax branch number of the customer (`00000` = head office). |
| `debxxxx` | STRING | Secondary salesperson (employee) code of the customer. |
| `debbusinesstype` | STRING | Business type code of the customer. |
| `debbusinessdesc` | STRING | Business type description of the customer. |
| `debactive` | INT64 | Active flag of the customer. |
| `debstatus` | INT64 | Status code of the customer (0 = normal). |
| `debexpiredate` | STRING | Expiry date of the customer record. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ak02` (`definitions/initial/mac5/create_all_table_raw_mac5_ak02.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ak02/deb/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ak02.deb`
LIMIT 100
```

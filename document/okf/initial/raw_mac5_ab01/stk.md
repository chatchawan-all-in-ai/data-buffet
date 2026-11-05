---
type: BigQuery Table
title: "stk"
description: "One row = one product (stock item), a record of source table `stk` (MAC5 for company `ab01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ab01&t=stk&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ab01
table_id: stk
tags: ["initial", "raw_mac5_ab01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_ab01.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_ab01.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ab01/stk/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `stk` table from MAC5 for company `ab01`; nothing is cleaned or deduplicated here. Table meaning: Product master of the MAC5 ERP: codes, barcodes, descriptions, units, VAT, GL accounts, default warehouse and sales grouping.

Read by: [validated_mac5.stk](/validated/validated_mac5/stk.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `stkcode` | STRING | Product (stock item) code. |
| `stkgroup` | STRING | Stock group code (joins `stg.stgcode`). |
| `stkcode2` | STRING | Secondary product code or short model name. |
| `stkdesct1` | STRING | Thai product description, line 1. |
| `stkdesct2` | STRING | Thai product description, line 2. |
| `stkdesct3` | STRING | Thai product description, line 3. |
| `stkdesce1` | STRING | English product description, line 1. |
| `stkdesce2` | STRING | English product description, line 2. |
| `stkdesce3` | STRING | English product description, line 3. |
| `stkmax` | FLOAT64 | Maximum stock level of the item. |
| `stkmin` | FLOAT64 | Minimum (reorder) stock level of the item. |
| `stkunit1` | INT64 | Unit number of the first alternate unit. |
| `stkunit2` | INT64 | Unit number of the second alternate unit. |
| `stkconv1` | FLOAT64 | Conversion factor of the first alternate unit to the base unit. |
| `stkconv2` | FLOAT64 | Conversion factor of the second alternate unit to the base unit. |
| `stksnsv` | INT64 | Stock-or-service type code of the item (`1`, `3`). |
| `stkuname0` | STRING | Name of unit 0 of the item (e.g. set, piece, kg). |
| `stkuname1` | STRING | Name of unit 1 of the item (e.g. set, piece, kg). |
| `stkuname2` | STRING | Name of unit 2 of the item (e.g. set, piece, kg). |
| `stkuname3` | STRING | Name of unit 3 of the item (e.g. set, piece, kg). |
| `stkuname4` | STRING | Name of unit 4 of the item (e.g. set, piece, kg). |
| `stkuname5` | STRING | Name of unit 5 of the item (e.g. set, piece, kg). |
| `stkqu1` | FLOAT64 | Quantity of unit 1 in the unit-conversion table. |
| `stkqu2` | FLOAT64 | Quantity of unit 2 in the unit-conversion table. |
| `stkqu3` | FLOAT64 | Quantity of unit 3 in the unit-conversion table. |
| `stkqu4` | FLOAT64 | Quantity of unit 4 in the unit-conversion table. |
| `stkqu5` | FLOAT64 | Quantity of unit 5 in the unit-conversion table. |
| `stkqe1` | FLOAT64 | Equivalent base-unit quantity of unit 1 in the unit-conversion table. |
| `stkqe2` | FLOAT64 | Equivalent base-unit quantity of unit 2 in the unit-conversion table. |
| `stkqe3` | FLOAT64 | Equivalent base-unit quantity of unit 3 in the unit-conversion table. |
| `stkqe4` | FLOAT64 | Equivalent base-unit quantity of unit 4 in the unit-conversion table. |
| `stkqe5` | FLOAT64 | Equivalent base-unit quantity of unit 5 in the unit-conversion table. |
| `stkqn1` | INT64 | Unit number of entry 1 in the unit-conversion table. |
| `stkqn2` | INT64 | Unit number of entry 2 in the unit-conversion table. |
| `stkqn3` | INT64 | Unit number of entry 3 in the unit-conversion table. |
| `stkqn4` | INT64 | Unit number of entry 4 in the unit-conversion table. |
| `stkqn5` | INT64 | Unit number of entry 5 in the unit-conversion table. |
| `stkvat` | FLOAT64 | VAT rate of the item in percent (e.g. 7). |
| `stkexpire` | INT64 | Expiry-date tracking flag of the item (0 = not tracked). |
| `stkhide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `stkuse2` | INT64 | Flag whether the second unit is used for the item (1 = used, 0 = not). |
| `stku2name` | STRING | Name of the second unit of the item. |
| `stkfx` | INT64 | Numeric setting code of the item (values 0 to 6). |
| `stkacp` | STRING | Purchase GL account code of the item (e.g. `511101`). |
| `stkacs` | STRING | Sales GL account code of the item (e.g. `411104`). |
| `stkacc` | STRING | GL account code of the item. |
| `stklock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `stkmemo` | STRING | Free-text memo on the item. |
| `stkacc1` | STRING | Additional GL account code 1 of the item. |
| `stkacc2` | STRING | Additional GL account code 2 of the item. |
| `stkeditlk` | STRING | Date and time the record was locked for editing. |
| `stkrefwe` | STRING | External reference code of the record. |
| `stkbarc1` | STRING | Barcode 1 of the item. |
| `stkbarc2` | STRING | Barcode 2 of the item. |
| `stkbarc3` | STRING | Barcode 3 of the item. |
| `stksortnt` | STRING | Thai sort key of the item (usually the Thai description). |
| `stksortne` | STRING | English sort key of the item. |
| `stkeditdt` | STRING | Date and time the record was last edited. |
| `stkstatus` | INT64 | Status code of the item (0 = normal). |
| `stksto` | STRING | Default warehouse code of the item (joins `sto.stocode`). |
| `stkeditmf` | STRING | User code of the person who last edited the record. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ab01` (`definitions/initial/mac5/create_all_table_raw_mac5_ab01.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ab01/stk/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ab01.stk`
LIMIT 100
```

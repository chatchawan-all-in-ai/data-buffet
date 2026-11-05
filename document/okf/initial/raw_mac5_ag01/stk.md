---
type: BigQuery Table
title: "stk"
description: "One row = one product (stock item), a record of source table `stk` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=stk&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: stk
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/stk/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `stk` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Product master of the MAC5 ERP: codes, barcodes, descriptions, units, VAT, GL accounts, default warehouse and sales grouping.

Read by: [validated_mac5.stk](/validated/validated_mac5/stk.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `STKcode` | STRING | Product (stock item) code. |
| `STKgroup` | STRING | Stock group code (joins `stg.stgcode`). |
| `STKcode2` | STRING | Secondary product code or short model name. |
| `STKdescT1` | STRING | Thai product description, line 1. |
| `STKdescT2` | STRING | Thai product description, line 2. |
| `STKdescT3` | STRING | Thai product description, line 3. |
| `STKdescE1` | STRING | English product description, line 1. |
| `STKdescE2` | STRING | English product description, line 2. |
| `STKdescE3` | STRING | English product description, line 3. |
| `STKmax` | FLOAT64 | Maximum stock level of the item. |
| `STKmin` | FLOAT64 | Minimum (reorder) stock level of the item. |
| `STKunit1` | INT64 | Unit number of the first alternate unit. |
| `STKunit2` | INT64 | Unit number of the second alternate unit. |
| `STKconv1` | FLOAT64 | Conversion factor of the first alternate unit to the base unit. |
| `STKconv2` | FLOAT64 | Conversion factor of the second alternate unit to the base unit. |
| `STKsnsv` | INT64 | Stock-or-service type code of the item (`1`, `3`). |
| `STKuname0` | STRING | Name of unit 0 of the item (e.g. set, piece, kg). |
| `STKuname1` | STRING | Name of unit 1 of the item (e.g. set, piece, kg). |
| `STKuname2` | STRING | Name of unit 2 of the item (e.g. set, piece, kg). |
| `STKuname3` | STRING | Name of unit 3 of the item (e.g. set, piece, kg). |
| `STKuname4` | STRING | Name of unit 4 of the item (e.g. set, piece, kg). |
| `STKuname5` | STRING | Name of unit 5 of the item (e.g. set, piece, kg). |
| `STKqU1` | FLOAT64 | Quantity of unit 1 in the unit-conversion table. |
| `STKqU2` | FLOAT64 | Quantity of unit 2 in the unit-conversion table. |
| `STKqU3` | FLOAT64 | Quantity of unit 3 in the unit-conversion table. |
| `STKqU4` | FLOAT64 | Quantity of unit 4 in the unit-conversion table. |
| `STKqU5` | FLOAT64 | Quantity of unit 5 in the unit-conversion table. |
| `STKqE1` | FLOAT64 | Equivalent base-unit quantity of unit 1 in the unit-conversion table. |
| `STKqE2` | FLOAT64 | Equivalent base-unit quantity of unit 2 in the unit-conversion table. |
| `STKqE3` | FLOAT64 | Equivalent base-unit quantity of unit 3 in the unit-conversion table. |
| `STKqE4` | FLOAT64 | Equivalent base-unit quantity of unit 4 in the unit-conversion table. |
| `STKqE5` | FLOAT64 | Equivalent base-unit quantity of unit 5 in the unit-conversion table. |
| `STKqN1` | INT64 | Unit number of entry 1 in the unit-conversion table. |
| `STKqN2` | INT64 | Unit number of entry 2 in the unit-conversion table. |
| `STKqN3` | INT64 | Unit number of entry 3 in the unit-conversion table. |
| `STKqN4` | INT64 | Unit number of entry 4 in the unit-conversion table. |
| `STKqN5` | INT64 | Unit number of entry 5 in the unit-conversion table. |
| `STKvat` | FLOAT64 | VAT rate of the item in percent (e.g. 7). |
| `STKexpire` | INT64 | Expiry-date tracking flag of the item (0 = not tracked). |
| `STKhide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `STKuse2` | INT64 | Flag whether the second unit is used for the item (1 = used, 0 = not). |
| `STKu2name` | STRING | Name of the second unit of the item. |
| `STKfx` | INT64 | Numeric setting code of the item (values 0 to 6). |
| `STKacP` | STRING | Purchase GL account code of the item (e.g. `511101`). |
| `STKacS` | STRING | Sales GL account code of the item (e.g. `411104`). |
| `STKacC` | STRING | GL account code of the item. |
| `STKlock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `STKmemo` | STRING | Free-text memo on the item. |
| `STKacC1` | STRING | Additional GL account code 1 of the item. |
| `STKacC2` | STRING | Additional GL account code 2 of the item. |
| `STKeditLK` | STRING | Date and time the record was locked for editing. |
| `STKrefWE` | STRING | External reference code of the record. |
| `STKbarC1` | STRING | Barcode 1 of the item. |
| `STKbarC2` | STRING | Barcode 2 of the item. |
| `STKbarC3` | STRING | Barcode 3 of the item. |
| `STKsortNT` | STRING | Thai sort key of the item (usually the Thai description). |
| `STKsortNE` | STRING | English sort key of the item. |
| `STKeditDT` | STRING | Date and time the record was last edited. |
| `STKstatus` | INT64 | Status code of the item (0 = normal). |
| `STKsto` | STRING | Default warehouse code of the item (joins `sto.stocode`). |
| `STKeditMF` | STRING | User code of the person who last edited the record. |
| `rowguid` | STRING | Row GUID that uniquely identifies the record in the source database. |
| `STKcode885` | STRING | EAN-13 barcode of the item (joins Master SKU `prd_barcode`). |
| `STKtype` | STRING | Product type name in Thai (e.g. ROTO above-ground water tank, BLOW water tank). |
| `STKSaleGrp` | STRING | Sales product group name (e.g. PE water tank, grease trap). |
| `STKSaleType` | STRING | Sales type of the item. |
| `STKSaleSup` | STRING | Sales supplier of the item. |
| `STKSaleGrpS1` | STRING | Sales sub-group 1 of the item. |
| `STKSaleGrpS2` | STRING | Sales sub-group 2 of the item. |
| `StkSub1` | STRING | Product sub-category 1 of the item. |
| `StkSub2` | STRING | Product sub-category 2 of the item. |
| `StkSub3` | STRING | Product sub-category 3 of the item. |
| `StkBrand` | STRING | Brand of the item. |
| `StkExpand` | STRING | Extended description of the item. |
| `StkLgGrp` | STRING | Logistics product group of the item (e.g. BLOW, HY, Accessorie). |
| `STKgroup_DGE` | STRING | DGE product group code of the item (e.g. `001`). |
| `STKgroup1_DGE_Report` | STRING | DGE report product group, level 1. |
| `STKgroup2_DGE_Report` | STRING | DGE report product group, level 2. |
| `STKgroup3_DGE_Report` | STRING | DGE report product group, level 3. |
| `Part_DGE` | STRING | DGE part code of the item. |
| `StkFPASS` | STRING | Pass flag of the item (1 = passed, 0 = not). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/stk/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.stk`
LIMIT 100
```

---
type: BigQuery Table
title: "stk"
description: "One row = one product (stock item) (per company), unique on (company_id, stkcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stk&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: stk
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stk.sqlx"
    title: "Dataform definition (validated/mac5/stk.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `stk` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product master of the MAC5 ERP: codes, barcodes, descriptions, units, VAT, GL accounts, default warehouse and sales grouping.
Used by: [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [onetime.Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md).

# Grain and key

One row per `company_id`, `stkcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
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
| `stkeditlk` | DATETIME | Date and time the record was locked for editing. |
| `stkrefwe` | STRING | External reference code of the record. |
| `stkbarc1` | STRING | Barcode 1 of the item. |
| `stkbarc2` | STRING | Barcode 2 of the item. |
| `stkbarc3` | STRING | Barcode 3 of the item. |
| `stksortnt` | STRING | Thai sort key of the item (usually the Thai description). |
| `stksortne` | STRING | English sort key of the item. |
| `stkeditdt` | DATETIME | Date and time the record was last edited. |
| `stkstatus` | INT64 | Status code of the item (0 = normal). |
| `stksto` | STRING | Default warehouse code of the item (joins `sto.stocode`). |
| `stkeditmf` | STRING | User code of the person who last edited the record. |
| `stkcode885` | STRING | EAN-13 barcode of the item (joins Master SKU `prd_barcode`). |
| `stktype` | STRING | Product type name in Thai (e.g. ROTO above-ground water tank, BLOW water tank). |
| `stksalegrp` | STRING | Sales product group name (e.g. PE water tank, grease trap). |
| `stksaletype` | STRING | Sales type of the item. |
| `stksalesup` | STRING | Sales supplier of the item. |
| `stksalegrps1` | STRING | Sales sub-group 1 of the item. |
| `stksalegrps2` | STRING | Sales sub-group 2 of the item. |
| `stksub1` | STRING | Product sub-category 1 of the item. |
| `stksub2` | STRING | Product sub-category 2 of the item. |
| `stksub3` | STRING | Product sub-category 3 of the item. |
| `stkbrand` | STRING | Brand of the item. |
| `stkexpand` | STRING | Extended description of the item. |
| `stklggrp` | STRING | Logistics product group of the item (e.g. BLOW, HY, Accessorie). |
| `stkgroup_dge` | STRING | DGE product group code of the item (e.g. `001`). |
| `stkgroup1_dge_report` | STRING | DGE report product group, level 1. |
| `stkgroup2_dge_report` | STRING | DGE report product group, level 2. |
| `stkgroup3_dge_report` | STRING | DGE report product group, level 3. |
| `part_dge` | STRING | DGE part code of the item. |
| `stkfpass` | STRING | Pass flag of the item (1 = passed, 0 = not). |

# How it is built

- Definition: `definitions/validated/mac5/stk.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.stk](/initial/raw_mac5_ag01/stk.md), [raw_mac5_aa05.stk](/initial/raw_mac5_aa05/stk.md), [raw_mac5_ab01.stk](/initial/raw_mac5_ab01/stk.md), [raw_mac5_ac02.stk](/initial/raw_mac5_ac02/stk.md), [raw_mac5_ak02.stk](/initial/raw_mac5_ak02/stk.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stkcode885 desc, stkeditdt desc, stkdesct1 desc, stkdesct2 desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `stkcode`.
- Approximate size (BigQuery metadata, 2026-10-31): 118,828 rows, 51.9 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stk`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stkcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stk`
GROUP BY company_id, stkcode
HAVING n > 1
```

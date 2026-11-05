---
type: BigQuery Table
title: "crm_nd_sd_price"
description: "One row = one ND/SD price record for a product, a record of source table `crm_nd_sd_price` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_nd_sd_price&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_nd_sd_price
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_nd_sd_price/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_nd_sd_price` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Product selling prices with list price, floor price, the normal-discount (ND) quantity tier and up to three special-discount (SD) tiers.

Read by: [validated_derp.crm_nd_sd_price](/validated/validated_derp/crm_nd_sd_price.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `nd_sd_price_id` | STRING | UUID of the ND/SD price record. |
| `product_id` | STRING | UUID of the product in the DERP product master. |
| `product_code` | STRING | Product (item) code. |
| `product_barcode` | STRING | Product barcode. |
| `effective_from` | STRING | Date the price takes effect. |
| `expiry_to` | STRING | Date the price expires (NULL = open-ended). |
| `status` | STRING | Price record status (`ACTIVE`, `INACTIVE` or `DELETE`). |
| `list_price_incl_vat` | FLOAT64 | List price including VAT, in THB. |
| `list_price_excl_vat` | FLOAT64 | List price excluding VAT, in THB. |
| `list_price_vat_rate` | FLOAT64 | VAT rate used for the list price, in percent. |
| `floor_pct` | FLOAT64 | Floor price as a percentage of the list price. |
| `floor_price_incl_vat` | FLOAT64 | Floor (minimum allowed) price including VAT, in THB. |
| `nd_min_qty` | INT64 | Minimum quantity for the ND (normal discount) price tier. |
| `nd_max_qty` | INT64 | Maximum quantity for the ND (normal discount) price tier. |
| `sd1_rate` | FLOAT64 | Discount rate of special-discount tier 1, in the unit given by `sd1_rate_type`. |
| `sd1_rate_type` | STRING | Unit of the tier-1 discount rate (`percent` or `bath` = THB amount). |
| `sd1_price_excl_vat` | FLOAT64 | Unit price excluding VAT for special-discount tier 1, in THB. |
| `sd1_min_qty` | INT64 | Minimum quantity for special-discount tier 1. |
| `sd1_max_qty` | INT64 | Maximum quantity for special-discount tier 1. |
| `sd2_rate` | FLOAT64 | Discount rate of special-discount tier 2, in the unit given by `sd2_rate_type`. |
| `sd2_rate_type` | STRING | Unit of the tier-2 discount rate (`percent` or `bath` = THB amount). |
| `sd2_price_excl_vat` | FLOAT64 | Unit price excluding VAT for special-discount tier 2, in THB. |
| `sd2_min_qty` | INT64 | Minimum quantity for special-discount tier 2. |
| `sd2_max_qty` | INT64 | Maximum quantity for special-discount tier 2. |
| `sd3_rate` | FLOAT64 | Discount rate of special-discount tier 3, in the unit given by `sd3_rate_type`. |
| `sd3_rate_type` | STRING | Unit of the tier-3 discount rate (`percent` or `bath` = THB amount). |
| `sd3_price_excl_vat` | FLOAT64 | Unit price excluding VAT for special-discount tier 3, in THB. |
| `sd3_min_qty` | INT64 | Minimum quantity for special-discount tier 3. |
| `sd3_max_qty` | INT64 | Maximum quantity for special-discount tier 3. |
| `bigpro_rate` | FLOAT64 | Discount rate of the big-promotion price, in the unit given by `bigpro_rate_type`. |
| `bigpro_rate_type` | STRING | Unit of the big-promotion discount rate (`percent` or `bath` = THB amount). |
| `bigpro_price_excl_vat` | FLOAT64 | Big-promotion unit price excluding VAT, in THB. |
| `remark` | STRING | Free-text remark on the price. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `deleted_at` | STRING | Timestamp when the record was soft-deleted (NULL while active). |
| `floor_rate_type` | STRING | Unit of the floor rate (`percent` or `bath` = THB amount). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_nd_sd_price/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_nd_sd_price`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_nd_sd_price`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

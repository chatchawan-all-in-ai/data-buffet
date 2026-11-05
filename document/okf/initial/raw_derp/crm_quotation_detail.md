---
type: BigQuery Table
title: "crm_quotation_detail"
description: "One row = one quotation line, a record of source table `crm_quotation_detail` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_quotation_detail&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_quotation_detail
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_quotation_detail/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_quotation_detail` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Product lines of sales quotations with prices, discounts, quantities and amounts, plus a parallel project price set.

Read by: [validated_derp.crm_quotation_detail](/validated/validated_derp/crm_quotation_detail.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_detail_id` | STRING | UUID of the quotation line. |
| `quotation_id` | STRING | UUID of the quotation in `crm_quotation`. |
| `quotation_date` | STRING | Quotation document date. |
| `quotation_no` | STRING | Quotation document number (e.g. `QT2607...` or `MDT2610...`). |
| `product_id` | STRING | UUID of the product in the DERP product master. |
| `product_code` | STRING | Product (item) code. |
| `promo_price` | FLOAT64 | Promotion (combo set) price per unit, in THB. |
| `unit_price` | FLOAT64 | Unit price of the product, in THB. |
| `unit` | STRING | Unit of measure (e.g. `EA`, `SET`, or Thai unit names). |
| `offer_unit_price` | FLOAT64 | Unit price offered to the customer, in THB. |
| `offer_promo_price` | FLOAT64 | Promotion (combo set) price offered to the customer, in THB. |
| `distribution_percent` | FLOAT64 | Distribution (dealer) margin rate, in percent. |
| `free_type` | BOOL | Flag marking a free (giveaway) line. |
| `list_price` | FLOAT64 | List price of the product per unit, in THB. |
| `normal_disc` | FLOAT64 | Normal discount rate, in percent. |
| `special_disc_1` | FLOAT64 | Special discount 1 rate, in percent. |
| `special_disc_2` | FLOAT64 | Special discount 2 rate, in percent. |
| `special_disc_3` | FLOAT64 | Special discount 3 rate, in percent. |
| `percent_disc` | FLOAT64 | Total discount rate of the line, in percent. |
| `qty_total` | INT64 | Quoted quantity. |
| `total_amount` | FLOAT64 | Line amount (quantity x offered price), in THB. |
| `distribution_amount` | FLOAT64 | Distribution (dealer) margin amount of the line, in THB. |
| `sale_type` | STRING | Line sale type (`normal`, `combo`, `ND`, general goods). |
| `order_sort` | INT64 | Display order of the line within the quotation. |
| `project_product_id` | STRING | Project price set: UUID of the product in the DERP product master. |
| `project_product_code` | STRING | Project price set: product (item) code. |
| `project_promo_price` | FLOAT64 | Project price set: promotion (combo set) price per unit, in THB. |
| `project_unit_price` | FLOAT64 | Project price set: unit price of the product, in THB. |
| `project_unit` | STRING | Project price set: unit of measure (e.g. `EA`, `SET`, or Thai unit names). |
| `project_offer_unit_price` | FLOAT64 | Project price set: unit price offered to the customer, in THB. |
| `project_offer_promo_price` | FLOAT64 | Project price set: promotion (combo set) price offered to the customer, in THB. |
| `project_distribution_percent` | FLOAT64 | Project price set: distribution (dealer) margin rate, in percent. |
| `project_free_type` | BOOL | Project price set: flag marking a free (giveaway) line. |
| `project_list_price` | FLOAT64 | Project price set: list price of the product per unit, in THB. |
| `project_normal_disc` | FLOAT64 | Project price set: normal discount rate, in percent. |
| `project_special_disc_1` | FLOAT64 | Project price set: special discount 1 rate, in percent. |
| `project_special_disc_2` | FLOAT64 | Project price set: special discount 2 rate, in percent. |
| `project_special_disc_3` | FLOAT64 | Project price set: special discount 3 rate, in percent. |
| `project_percent_disc` | FLOAT64 | Project price set: total discount rate of the line, in percent. |
| `project_qty_total` | INT64 | Project price set: quoted quantity. |
| `project_total_amount` | FLOAT64 | Project price set: line amount (quantity x offered price), in THB. |
| `project_distribution_amount` | FLOAT64 | Project price set: distribution (dealer) margin amount of the line, in THB. |
| `project_sale_type` | STRING | Project price set: line sale type (`normal`, `combo`, `ND`, general goods). |
| `project_order_sort` | INT64 | Project price set: display order of the line within the quotation. |
| `mac5_id` | INT64 | Numeric ID of the quotation in MAC5. |
| `mac5_detail_id` | INT64 | Numeric ID of the quotation line in MAC5. |
| `mac5_code` | STRING | Document code of the quotation in MAC5. |
| `revamp_id` | INT64 | Numeric ID of the quotation in the Revamp system. |
| `revamp_detail_id` | INT64 | Numeric ID of the quotation line in the Revamp system. |
| `revamp_code` | STRING | Document code of the quotation in the Revamp system. |
| `d365_id` | INT64 | Numeric ID of the quotation in D365. |
| `d365_detail_id` | INT64 | Numeric ID of the quotation line in D365. |
| `d365_code` | STRING | Document code of the quotation in D365. |
| `ref_1_id` | INT64 | Numeric ID of the quotation in reference system 1. |
| `ref_1_detail_id` | INT64 | Numeric ID of the quotation line in reference system 1. |
| `ref_1_code` | STRING | Document code of the quotation in reference system 1. |
| `ref_2_id` | INT64 | Numeric ID of the quotation in reference system 2. |
| `ref_2_detail_id` | INT64 | Numeric ID of the quotation line in reference system 2. |
| `ref_2_code` | STRING | Document code of the quotation in reference system 2. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `combo_set_id` | STRING | UUID of the combo set (product bundle) the line belongs to. |
| `combo_set_code` | STRING | Code of the combo set (product bundle) the line belongs to (e.g. `COMBOSET00014`). |
| `project_combo_set_id` | STRING | Project price set: UUID of the combo set (product bundle) the line belongs to. |
| `project_combo_set_code` | STRING | Project price set: code of the combo set (product bundle) the line belongs to (e.g. `COMBOSET00014`). |
| `bu_code` | STRING | Business unit code (see `crm_business_unit.bu_code`, e.g. `01` = PE). |
| `bu_name` | STRING | Business unit name. |
| `project_bu_code` | STRING | Project price set: business unit code (see `crm_business_unit.bu_code`, e.g. `01` = PE). |
| `project_bu_name` | STRING | Project price set: business unit name. |
| `bu_id` | STRING | UUID of the business unit of the line. |
| `project_bu_id` | STRING | Project price set: UUID of the business unit of the line. |
| `sales_id` | STRING | UUID of the salesperson of the line. |
| `sales_code` | STRING | Employee number of the salesperson. |
| `sales_name` | STRING | Name of the salesperson. |
| `parent_quotation_detail_id` | STRING | UUID of the parent quotation line (for sub-lines). |
| `lv` | INT64 | Nesting level of the line (1 = top-level line). |
| `project_mac5_code` | STRING | Project price set: MAC5 document code of the line. |
| `distribution_amount_per_unit` | FLOAT64 | Distribution (dealer) margin amount per unit, in THB. |
| `qty_remaining` | INT64 | Quantity not yet used on sales orders. |
| `qty_used` | INT64 | Quantity already used on sales orders. |
| `product_description` | STRING | Free-text product description of the line. |
| `freebie_main_detail_id` | STRING | UUID of the main quotation line a free item is attached to. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_quotation_detail/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_quotation_detail`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_quotation_detail`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

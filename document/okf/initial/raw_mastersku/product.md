---
type: BigQuery Table
title: "product"
description: "One row = one product (SKU), a record of source table `product` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=product&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mastersku
table_id: product
tags: ["initial", "raw_mastersku", "mastersku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx"
    title: "Dataform definition (initial/mastersku/create_all_table_raw_mastersku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mastersku/product/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `product` table from MASTERSKU; nothing is cleaned or deduplicated here. Table meaning: Products (SKUs) of the old product master MASTERSKU, with SKU code, name, barcodes, sales unit, brand, category, vendor, product group and status. Used by: [validated_mastersku.product](/validated/validated_mastersku/product.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `prd_id` | STRING | Unique identifier (UUID) of the product. |
| `prd_sku` | STRING | Master SKU code of the product (`MSKU` + 10 digits). |
| `prd_description` | STRING | Product name/description. |
| `prd_d365_sku` | STRING | Item number of the product in Dynamics 365. |
| `prd_item_text` | STRING | Free-text item text of the product. |
| `prd_item_code` | STRING | Item code of the product in the MAC5 ERP. |
| `prd_stopped_sate` | STRING | Date the product was stopped (discontinued). |
| `prd_made_to_order` | STRING | Made-to-order indicator of the product. |
| `prd_sale_unite` | STRING | Sales unit of the product (e.g. `EA`, `SET`, `ชุด`, `ชิ้น`). |
| `prd_tag` | STRING | Search tags of the product as JSON (`{"mypro_tag":[...]}`). |
| `prd_universal_barcode` | STRING | Universal (GS1/EAN) barcode of the product. |
| `prd_internal_barcode` | STRING | Internal barcode/code assigned to the product. |
| `prd_cat_id` | STRING | Category of the product (FK to `category.cat_id`). |
| `prd_filter1` | STRING | First search filter value of the product. |
| `prd_filter2` | STRING | Second search filter value of the product. |
| `prd_brand_id` | STRING | Brand of the product (FK to `brand.bra_id`). |
| `prd_size` | STRING | Size of the product. |
| `prd_line` | STRING | Product line. |
| `prd_color` | STRING | Color of the product. |
| `prd_model` | STRING | Model of the product. |
| `prd_dimension1` | STRING | Value of variant dimension 1 of the product (label set by its product group `pg_dimension1`). |
| `prd_dimension2` | STRING | Value of variant dimension 2 of the product (label set by its product group `pg_dimension2`). |
| `prd_dimension3` | STRING | Value of variant dimension 3 of the product (label set by its product group `pg_dimension3`). |
| `prd_dimension4` | STRING | Value of variant dimension 4 of the product (label set by its product group `pg_dimension4`). |
| `prd_vendor_id` | STRING | Vendor (supplier) of the product (FK to `vendor.vd_id`). |
| `prd_is_active` | BOOL | Product active flag (product status is active). |
| `prd_is_use` | BOOL | Product open-for-sale flag. |
| `prd_created_date` | STRING | Timestamp when the record was created. |
| `prd_created_by` | STRING | Identifier of the user who created the record. |
| `prd_updated_date` | STRING | Timestamp when the record was last updated. |
| `prd_updated_by` | STRING | Identifier of the user who last updated the record. |
| `prd_pg_id` | STRING | Product group of the product (FK to `product_group.pg_id`). |
| `prd_ps_id` | STRING | Product status (FK to `product_status.ps_id`; e.g. On, Off, Draft, Pending, Approve, Reject). |
| `prd_id_source` | STRING | Product identifier in the system the product was imported from (barcode-like code). |
| `prd_mc_id` | STRING | Merchandise category identifier of the product. |
| `prd_diminsion_data` | STRING | Variant dimension labels and values as JSON (`{"dimFeild":[{"label","value"}]}`). |
| `prd_pas_id` | STRING | Admin review status of the product (FK to `product_admin_status.pas_id`; e.g. new, edit, duplicate, open, close, delete). |
| `prd_barcode` | STRING | Barcode of the product, used to match MAC5 products (`STKcode885`). |
| `prd_reject_remark` | STRING | Remark explaining why the product was rejected. |
| `prd_ref_mp_id` | STRING | Reference to the master product record this product was created from. |
| `prd_is_combo` | BOOL | Flag marking the product as a combo (bundle) set. |
| `prd_combo_price` | FLOAT64 | Selling price of the combo set. |
| `prd_is_time` | BOOL | Flag marking the combo as time-limited (valid between `prd_combo_start` and `prd_combo_end`). |
| `prd_combo_start` | STRING | Start date-time of the combo offer. |
| `prd_combo_end` | STRING | End date-time of the combo offer. |
| `prd_total_combo_price` | FLOAT64 | Total selling price of all items in the combo. |
| `prd_total_cost_combo_price` | FLOAT64 | Total cost price of all items in the combo. |
| `prd_barcode_format` | STRING | Barcode format of the product (e.g. `GTIN-13 / EAN-13`, `GTIN-12 / UPC-A`). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mastersku` (`definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mastersku/product/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mastersku.product`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mastersku.product`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

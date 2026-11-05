---
type: BigQuery Table
title: "product"
description: "One row = one product (SKU) from source table `product`, unique on (prd_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: product
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product.sqlx"
    title: "Dataform definition (validated/mastersku/product.sqlx)"
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

Validated copy of MASTERSKU `product`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Products (SKUs) of the old product master MASTERSKU, with SKU code, name, barcodes, sales unit, brand, category, vendor, product group and status.
Used by: [curated_mastersku.curated_product](/curated/curated_mastersku/curated_product.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md).

# Grain and key

One row per `prd_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `prd_created_date` | DATETIME | Timestamp when the record was created. |
| `prd_created_by` | STRING | Identifier of the user who created the record. |
| `prd_updated_date` | DATETIME | Timestamp when the record was last updated. |
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
| `prd_combo_start` | DATETIME | Start date-time of the combo offer. |
| `prd_combo_end` | DATETIME | End date-time of the combo offer. |
| `prd_total_combo_price` | FLOAT64 | Total selling price of all items in the combo. |
| `prd_total_cost_combo_price` | FLOAT64 | Total cost price of all items in the combo. |
| `prd_barcode_format` | STRING | Barcode format of the product (e.g. `GTIN-13 / EAN-13`, `GTIN-12 / UPC-A`). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product](/initial/raw_mastersku/product.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `prd_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT prd_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product`
GROUP BY prd_id
HAVING n > 1
```

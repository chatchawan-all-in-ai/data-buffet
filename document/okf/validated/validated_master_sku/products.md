---
type: BigQuery Table
title: "products"
description: "One row = one product (SKU) from source table `products`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=products&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: products
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/products.sqlx"
    title: "Dataform definition (validated/master_sku/products.sqlx)"
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

Validated copy of MASTER_SKU `products`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Products (SKUs) of the master_sku 3.0 product master, with master SKU code, MAC5 and Dynamics 365 cross-reference codes, barcodes, texts, dimensions, units of measure, classification groups and statuses.
Used by: [curated_master_sku.curated_products](/curated/curated_master_sku/curated_products.md), [curated_master_sku.product_for_aisearch_v3](/curated/curated_master_sku/product_for_aisearch_v3.md).

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the product. |
| `product_code` | STRING | Product code. |
| `sku_code` | STRING | SKU code. |
| `master_sku_code` | STRING | Master SKU code of the product (`MSKU` + 10 digits). |
| `mac5_code` | STRING | Item code of the product in the MAC5 ERP. |
| `d365_code` | STRING | Item number of the product in Dynamics 365 (DERP). |
| `d365_size` | STRING | Dynamics 365 size dimension of the product (zero-padded, e.g. `01000L`). |
| `d365_style` | STRING | Dynamics 365 style dimension of the product (e.g. `STDA`). |
| `d365_color` | STRING | Dynamics 365 color dimension of the product. |
| `d365_configuration` | STRING | Dynamics 365 configuration dimension of the product (e.g. `STDA`). |
| `d365_variant` | STRING | Dynamics 365 variant number of the product. |
| `base_sku_id` | STRING | Base SKU this product is a variant or pack of (FK to `products.id`). |
| `universal_barcode` | STRING | Universal (GS1/EAN) barcode of the product. |
| `universal_barcode_history` | STRING | Previous universal barcodes of the product (JSON array). |
| `internal_barcode` | STRING | Internal barcode/code assigned to the product. |
| `universal_barcode_format_id` | STRING | Format of the universal barcode (FK to `common_codes.id` of type `barcode-format`). |
| `internal_barcode_format_id` | STRING | Format of the internal barcode (FK to `common_codes.id` of type `barcode-format`). |
| `name` | STRING | Product name. |
| `description_short` | STRING | Short product description. |
| `description` | STRING | Product description. |
| `property` | STRING | Product properties text. |
| `detail` | STRING | Product detail text. |
| `instruction` | STRING | Usage instructions. |
| `recommendation` | STRING | Usage recommendations. |
| `caution` | STRING | Caution/warning text. |
| `installation` | STRING | Installation instructions. |
| `transportation` | STRING | Transportation/handling instructions. |
| `stack_over` | STRING | Stacking limit instructions. |
| `warranty_detail` | STRING | Warranty terms. |
| `warranty_period` | STRING | Warranty period (e.g. `1Y`, `20 Y`). |
| `shelf_life_period_days` | INT64 | Shelf life of the product in days. |
| `tis_no` | STRING | Thai Industrial Standard (TIS) number of the product. |
| `tis_permit_no` | STRING | Thai Industrial Standard (TIS) permit (licence) number. |
| `other_certification` | STRING | Other certifications of the product. |
| `net_weight` | FLOAT64 | Net weight of the product (unit in `weight_unit_id`). |
| `net_width` | FLOAT64 | Net (product) width (unit in `length_unit_id`). |
| `net_length` | FLOAT64 | Net (product) length (unit in `length_unit_id`). |
| `net_height` | FLOAT64 | Net (product) height (unit in `length_unit_id`). |
| `gross_weight` | FLOAT64 | Gross (packed) weight of the product (unit in `weight_unit_id`). |
| `gross_width` | FLOAT64 | Package width (unit in `length_package_unit_id`). |
| `gross_length` | FLOAT64 | Package length (unit in `length_package_unit_id`). |
| `gross_height` | FLOAT64 | Package height (unit in `length_package_unit_id`). |
| `weight_unit_id` | STRING | Unit of the net and gross weights (FK to `common_codes.id` of type `uom-weight`). |
| `length_unit_id` | STRING | Unit of the net dimensions (FK to `common_codes.id` of type `uom-length`). |
| `length_package_unit_id` | STRING | Unit of the package dimensions (FK to `common_codes.id` of type `uom-length`). |
| `volume_unit_id` | STRING | Unit of the volume (FK to `common_codes.id` of type `uom-volume`). |
| `volume` | FLOAT64 | Volume of the product (unit in `volume_unit_id`). |
| `uom_id` | STRING | Base unit of measure of the product (FK to `common_codes.id`). |
| `uom_display_id` | STRING | Display unit for the base unit of measure (FK to `common_codes.id`). |
| `is_lowest_uom` | BOOL | Flag marking the base unit as the lowest unit of measure. |
| `uom_conversion` | FLOAT64 | Conversion factor of the base unit of measure. |
| `uom_sales_id` | STRING | Sales unit of measure (FK to `common_codes.id` of type `sales-unit`). |
| `uom_sales_conversion` | FLOAT64 | Conversion factor from the sales unit to the base unit. |
| `uom_sales_display_id` | STRING | Display unit for the sales unit (FK to `common_codes.id`). |
| `uom_purchase_id` | STRING | Purchase unit of measure (FK to `common_codes.id` of type `purchase-unit`). |
| `uom_purchase_conversion` | FLOAT64 | Conversion factor from the purchase unit to the base unit. |
| `uom_purchase_display_id` | STRING | Display unit for the purchase unit (FK to `common_codes.id`). |
| `uom_inventory_id` | STRING | Inventory unit of measure (FK to `common_codes.id` of type `inventory-unit`). |
| `uom_inventory_conversion` | FLOAT64 | Conversion factor from the inventory unit to the base unit. |
| `uom_inventory_display_id` | STRING | Display unit for the inventory unit (FK to `common_codes.id`). |
| `uom_bom_id` | STRING | Bill-of-materials unit of measure (FK to `common_codes.id` of type `bom-unit`). |
| `uom_bom_conversion` | FLOAT64 | Conversion factor from the bill-of-materials unit to the base unit. |
| `uom_bom_display_id` | STRING | Display unit for the bill-of-materials unit (FK to `common_codes.id`). |
| `search_name` | STRING | Search name of the product. |
| `tags` | STRING | Search tags of the product (JSON array). |
| `supplier_country` | STRING | Country of the supplier (country of origin). |
| `model` | STRING | Product model. |
| `series` | STRING | Product series name. |
| `material` | STRING | Main material of the product. |
| `package_shape` | STRING | Packaging shape of the product. |
| `shape` | STRING | Shape of the product. |
| `shade` | STRING | Shade of the product color. |
| `pattern` | STRING | Pattern of the product surface. |
| `color_descriptor_id` | STRING | Color descriptor of the product (FK to `common_codes.id` of type `color-descriptor`). |
| `fob` | FLOAT64 | Free-on-board (FOB) price of the product. |
| `business_unit_id` | STRING | Business unit that owns the product (FK to `common_codes.id`). |
| `brand_id` | STRING | Brand of the product (FK to `brands.id`). |
| `brand_vendor_id` | STRING | Brand-vendor link of the product (FK to `brand_vendors.id`); gives the product vendor. |
| `category_id` | STRING | Category of the product (FK to `categories.id`). |
| `product_type_id` | STRING | Product type (FK to `common_codes.id` of type `product-type`: Item, Service). |
| `product_sub_type_id` | STRING | Product sub-type (FK to `common_codes.id` of type `product-sub-type`: Product, ProductMaster). |
| `production_type_id` | STRING | Production type (FK to `common_codes.id` of type `production-type`, e.g. Main Item, Co Product, Formula). |
| `specification_group_id` | STRING | Specification group (product family) of the product (FK to `spec_groups.id`); equals the old MASTERSKU product group id. |
| `specification_attributes` | STRING | Variant attribute values of the product as a JSON array of `{id, label, value}`. |
| `product_group_id` | STRING | Product group of the product. |
| `sales_group_id` | STRING | Sales group of the product. |
| `cost_group_id` | STRING | Cost group of the product. |
| `production_group_id` | STRING | Production group of the product. |
| `production_sale_group_id` | STRING | Production sales group of the product. |
| `marketing_group_id` | STRING | Marketing group of the product. |
| `purchase_group_id` | STRING | Purchase group of the product. |
| `account_group_id` | STRING | Account group of the product. |
| `pricing_group_id` | STRING | Pricing group of the product. |
| `sales_status` | STRING | Sales status of the product (`Active` = open for sale, `Inactive`). |
| `sales_status_remark` | STRING | Remark on the latest sales status change. |
| `sales_status_date` | DATETIME | Date-time of the latest sales status change. |
| `production_status` | STRING | Production status of the product. |
| `production_status_remark` | STRING | Remark on the latest production status change. |
| `production_status_date` | DATETIME | Date-time of the latest production status change. |
| `product_status` | STRING | Product status (`Active`, `Inactive`). |
| `product_status_remark` | STRING | Remark on the latest product status change (e.g. rejection reason). |
| `product_status_date` | DATETIME | Date-time of the latest product status change. |
| `search_text` | STRING | Concatenated searchable text of the product (name, SKU code, barcodes, model, series). |
| `search_doc` | STRING | Search document text of the product. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/master_sku/products.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.products](/initial/raw_master_sku/products.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 129,721 rows, 307.2 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.products`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.products`
GROUP BY id
HAVING n > 1
```

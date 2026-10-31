---
type: BigQuery Table
title: "products"
description: "One row = one cleaned copy of the source table `products`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=products&page=table"
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

Validated copy of MASTER_SKU `products`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_master_sku.curated_products](/curated/curated_master_sku/curated_products.md), [curated_master_sku.product_for_aisearch_v3](/curated/curated_master_sku/product_for_aisearch_v3.md).

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Surrogate identifier from the source system (the primary key). |
| `product_code` | STRING | Meaning not documented in the repo. |
| `sku_code` | STRING | Meaning not documented in the repo. |
| `master_sku_code` | STRING | Meaning not documented in the repo. |
| `mac5_code` | STRING | Meaning not documented in the repo. |
| `d365_code` | STRING | Meaning not documented in the repo. |
| `d365_size` | STRING | Meaning not documented in the repo. |
| `d365_style` | STRING | Meaning not documented in the repo. |
| `d365_color` | STRING | Meaning not documented in the repo. |
| `d365_configuration` | STRING | Meaning not documented in the repo. |
| `d365_variant` | STRING | Meaning not documented in the repo. |
| `base_sku_id` | STRING | Meaning not documented in the repo. |
| `universal_barcode` | STRING | Meaning not documented in the repo. |
| `universal_barcode_history` | STRING | Meaning not documented in the repo. |
| `internal_barcode` | STRING | Meaning not documented in the repo. |
| `universal_barcode_format_id` | STRING | Meaning not documented in the repo. |
| `internal_barcode_format_id` | STRING | Meaning not documented in the repo. |
| `name` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `description_short` | STRING | Meaning not documented in the repo. |
| `description` | STRING | Meaning not documented in the repo. |
| `property` | STRING | Meaning not documented in the repo. |
| `detail` | STRING | Meaning not documented in the repo. |
| `instruction` | STRING | Meaning not documented in the repo. |
| `recommendation` | STRING | Meaning not documented in the repo. |
| `caution` | STRING | Meaning not documented in the repo. |
| `installation` | STRING | Meaning not documented in the repo. |
| `transportation` | STRING | Meaning not documented in the repo. |
| `stack_over` | STRING | Meaning not documented in the repo. |
| `warranty_detail` | STRING | Meaning not documented in the repo. |
| `warranty_period` | STRING | Meaning not documented in the repo. |
| `shelf_life_period_days` | INT64 | Meaning not documented in the repo. |
| `tis_no` | STRING | Meaning not documented in the repo. |
| `tis_permit_no` | STRING | Meaning not documented in the repo. |
| `other_certification` | STRING | Meaning not documented in the repo. |
| `net_weight` | FLOAT64 | Meaning not documented in the repo. |
| `net_width` | FLOAT64 | Meaning not documented in the repo. |
| `net_length` | FLOAT64 | Meaning not documented in the repo. |
| `net_height` | FLOAT64 | Meaning not documented in the repo. |
| `gross_weight` | FLOAT64 | Meaning not documented in the repo. |
| `gross_width` | FLOAT64 | Meaning not documented in the repo. |
| `gross_length` | FLOAT64 | Meaning not documented in the repo. |
| `gross_height` | FLOAT64 | Meaning not documented in the repo. |
| `weight_unit_id` | STRING | Meaning not documented in the repo. |
| `length_unit_id` | STRING | Meaning not documented in the repo. |
| `length_package_unit_id` | STRING | Meaning not documented in the repo. |
| `volume_unit_id` | STRING | Meaning not documented in the repo. |
| `volume` | FLOAT64 | Meaning not documented in the repo. |
| `uom_id` | STRING | Meaning not documented in the repo. |
| `uom_display_id` | STRING | Meaning not documented in the repo. |
| `is_lowest_uom` | BOOL | Meaning not documented in the repo. |
| `uom_conversion` | FLOAT64 | Meaning not documented in the repo. |
| `uom_sales_id` | STRING | Meaning not documented in the repo. |
| `uom_sales_conversion` | FLOAT64 | Meaning not documented in the repo. |
| `uom_sales_display_id` | STRING | Meaning not documented in the repo. |
| `uom_purchase_id` | STRING | Meaning not documented in the repo. |
| `uom_purchase_conversion` | FLOAT64 | Meaning not documented in the repo. |
| `uom_purchase_display_id` | STRING | Meaning not documented in the repo. |
| `uom_inventory_id` | STRING | Meaning not documented in the repo. |
| `uom_inventory_conversion` | FLOAT64 | Meaning not documented in the repo. |
| `uom_inventory_display_id` | STRING | Meaning not documented in the repo. |
| `uom_bom_id` | STRING | Meaning not documented in the repo. |
| `uom_bom_conversion` | FLOAT64 | Meaning not documented in the repo. |
| `uom_bom_display_id` | STRING | Meaning not documented in the repo. |
| `search_name` | STRING | Meaning not documented in the repo. |
| `tags` | STRING | Meaning not documented in the repo. |
| `supplier_country` | STRING | Meaning not documented in the repo. |
| `model` | STRING | Meaning not documented in the repo. |
| `series` | STRING | Meaning not documented in the repo. |
| `material` | STRING | Meaning not documented in the repo. |
| `package_shape` | STRING | Meaning not documented in the repo. |
| `shape` | STRING | Meaning not documented in the repo. |
| `shade` | STRING | Meaning not documented in the repo. |
| `pattern` | STRING | Meaning not documented in the repo. |
| `color_descriptor_id` | STRING | Meaning not documented in the repo. |
| `fob` | FLOAT64 | Meaning not documented in the repo. |
| `business_unit_id` | STRING | Meaning not documented in the repo. |
| `brand_id` | STRING | Meaning not documented in the repo. |
| `brand_vendor_id` | STRING | Meaning not documented in the repo. |
| `category_id` | STRING | Meaning not documented in the repo. |
| `product_type_id` | STRING | Meaning not documented in the repo. |
| `product_sub_type_id` | STRING | Meaning not documented in the repo. |
| `production_type_id` | STRING | Meaning not documented in the repo. |
| `specification_group_id` | STRING | Meaning not documented in the repo. |
| `specification_attributes` | STRING | Meaning not documented in the repo. |
| `product_group_id` | STRING | Meaning not documented in the repo. |
| `sales_group_id` | STRING | Meaning not documented in the repo. |
| `cost_group_id` | STRING | Meaning not documented in the repo. |
| `production_group_id` | STRING | Meaning not documented in the repo. |
| `production_sale_group_id` | STRING | Meaning not documented in the repo. |
| `marketing_group_id` | STRING | Meaning not documented in the repo. |
| `purchase_group_id` | STRING | Meaning not documented in the repo. |
| `account_group_id` | STRING | Meaning not documented in the repo. |
| `pricing_group_id` | STRING | Meaning not documented in the repo. |
| `sales_status` | STRING | Meaning not documented in the repo. |
| `sales_status_remark` | STRING | Meaning not documented in the repo. |
| `sales_status_date` | DATETIME | Meaning not documented in the repo. |
| `production_status` | STRING | Meaning not documented in the repo. |
| `production_status_remark` | STRING | Meaning not documented in the repo. |
| `production_status_date` | DATETIME | Meaning not documented in the repo. |
| `product_status` | STRING | Meaning not documented in the repo. |
| `product_status_remark` | STRING | Meaning not documented in the repo. |
| `product_status_date` | DATETIME | Meaning not documented in the repo. |
| `search_text` | STRING | Meaning not documented in the repo. |
| `search_doc` | STRING | Meaning not documented in the repo. |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
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

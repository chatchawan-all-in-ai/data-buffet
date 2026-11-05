---
type: BigQuery Table
title: "product_for_aisearch_v3"
description: "One row = one product (master SKU) per run date, in the shape the AI search index reads: an id plus a structData struct."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_master_sku&t=product_for_aisearch_v3&page=table"
project_id: databuffet-nonprd
dataset_id: curated_master_sku
table_id: product_for_aisearch_v3
tags: ["curated", "curated_master_sku", "master_sku", "MASTER_SKU", "AI search"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/master_sku/product_for_aisearch_v3.sqlx"
    title: "Dataform definition (curated/master_sku/product_for_aisearch_v3.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Daily feed of the product catalogue for AI search, built directly from the master_sku 3.0 validated tables. It is the master_sku 3.0 counterpart of [product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md) (legacy MASTERSKU source). The struct has 15 fields.

# Grain and key

One row per `id` (master SKU code) per `asatdate` (run date). Only products whose `asatdate` in validated_master_sku.products is within run_date-1 and run_date are included (latest `updated_at` row per master_sku_code, placeholders without a code dropped).

# Schema

| Column | Type | Description |
|---|---|---|
| `asatdate` | DATE | Run date (CURRENT_DATE in Asia/Bangkok) when the row was generated; partition column. Each day replaces its own partition. |
| `id` | STRING | Master SKU code (products.master_sku_code); cluster column. One row per SKU per run date. |
| `structData` | STRUCT<product_name STRING, sku_code STRING, sales_unit STRING, product_tags_json STRING, barcode STRING, cat_name STRING, brand_name STRING, vd_name STRING, product_status STRING, product_dimensions_json STRING, product_description STRING, product_series STRING, product_model STRING, product_material STRING, product_shape STRING> | Payload struct read by the AI search index. Fields: product_name (products.name), sku_code (master_sku_code), sales_unit (curated_products prdSaleUnite rule), product_tags_json (products.tags as-is), barcode (universal_barcode), cat_name (categories.name), brand_name (brands.name, else the brand of brand_vendors), vd_name (vendors.name via brand_vendors), product_status ('Approve' when product_status and sales_status are both 'Active', else 'Non-Approve'), product_dimensions_json ({"dimFeild":[{label,value}]} from specification_attributes), product_description (detail, NULL when it is only a short product code), product_series, product_model (model, else variant 'โมเดล', else 'รุ่นสินค้า'), product_material (material, else variant 'วัสดุ' without placeholders 'โปรดระบุ', '-', '0'), product_shape (package_shape). |

# How it is built

- Definition: `definitions/curated/master_sku/product_for_aisearch_v3.sqlx` (`type: "operations"`, tags `curated`); the operation owns this table.
- Reads: [validated_master_sku.products](/validated/validated_master_sku/products.md), [validated_master_sku.common_codes](/validated/validated_master_sku/common_codes.md), [validated_master_sku.brands](/validated/validated_master_sku/brands.md), [validated_master_sku.categories](/validated/validated_master_sku/categories.md), [validated_master_sku.brand_vendors](/validated/validated_master_sku/brand_vendors.md), [validated_master_sku.vendors](/validated/validated_master_sku/vendors.md).
- Operations action (`type: "operations"`, tag `curated`, after `curated_schema_master_sku`): builds TEMP tables, creates the target on first run (`CREATE TABLE IF NOT EXISTS`, partition `asatdate`, cluster `id`), then in one transaction DELETEs the current run date's partition and INSERTs the new rows (atomic; if the INSERT fails the old partition stays).

# Examples

Latest snapshot of the feed.

```sql
SELECT id, structData.product_name, structData.brand_name, structData.product_status
FROM `databuffet-nonprd.curated_master_sku.product_for_aisearch_v3`
WHERE asatdate = (SELECT MAX(asatdate) FROM `databuffet-nonprd.curated_master_sku.product_for_aisearch_v3`)
LIMIT 100
```

Approved and non-approved product counts in the latest snapshot.

```sql
SELECT structData.product_status AS status, COUNT(*) AS n
FROM `databuffet-nonprd.curated_master_sku.product_for_aisearch_v3`
WHERE asatdate = (SELECT MAX(asatdate) FROM `databuffet-nonprd.curated_master_sku.product_for_aisearch_v3`)
GROUP BY status
```

---
type: BigQuery Table
title: "product_for_aisearch"
description: "One row = one product SKU per run date, in the shape the AI search index reads: an id plus a structData struct (legacy MASTERSKU source)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mastersku&t=product_for_aisearch&page=table"
project_id: databuffet-nonprd
dataset_id: curated_mastersku
table_id: product_for_aisearch
tags: ["curated", "curated_mastersku", "mastersku", "MASTERSKU", "AI search"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/mastersku/product_for_aisearch.sqlx"
    title: "Dataform definition (curated/mastersku/product_for_aisearch.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily feed of the product catalogue for AI search, built from [curated_product](/curated/curated_mastersku/curated_product.md) joined with product_detail, brand, category, vendor and unit lookups of the legacy MASTERSKU source. The master_sku 3.0 shadow is [product_for_aisearch_v3](/curated/curated_master_sku/product_for_aisearch_v3.md). Read by the external AI search ingest, not by other objects in this repo.

# Grain and key

One row per `id` (prdSku) per `asatdate` (run date). Only products whose curated_product `asatdate` is within run_date-1 and run_date are included (no extra dedup; curated_product is expected to have one row per SKU).

# Schema

| Column | Type | Description |
|---|---|---|
| `asatdate` | DATE | Run date (CURRENT_DATE in Asia/Bangkok) when the row was generated; partition-like day key (the table is not declared partitioned here; the operation deletes and re-inserts the run date). |
| `id` | STRING | Product SKU (curated_product.prdSku); one row per SKU per run date. |
| `structData` | STRUCT<product_name STRING, sku_code STRING, sales_unit STRING, product_tags_json STRING, barcode STRING, cat_name STRING, brand_name STRING, vd_name STRING, product_status STRING, product_dimensions_json STRING, product_description STRING, product_series STRING, product_model STRING, product_material STRING, product_shape STRING, package_width FLOAT64, package_width_unit STRING, package_length FLOAT64, package_length_unit STRING, package_height FLOAT64, package_height_unit STRING, product_weight_net FLOAT64, product_weight_net_unit STRING, product_weight_gross FLOAT64, product_weight_gross_unit STRING, special_specifications_json STRING> | Payload struct read by the AI search index. Fields: product_name (prdDescription), sku_code (prdSku), sales_unit (prdSaleUnite), product_tags_json (prdTag), barcode (prdUniversalBarcode), cat_name (category.cat_name), brand_name (brand.bra_name, else bra_name_th), vd_name (vendor.vd_name), product_status ('Approve' when prdIsActive, prdIsUse and product_detail.pd_is_system are all TRUE, else 'Non-Approve'), product_dimensions_json (prdDiminsionData), product_description/series/model/material/shape (pd_detail, pd_series, pd_model, pd_material, pd_shape), package_width/length/height (pd_package_wide/long/hight) with their unit names, product_weight_net/gross with unit names, special_specifications_json (pd_spacific_fields). |

# How it is built

- Definition: `definitions/curated/mastersku/product_for_aisearch.sqlx` (`type: "operations"`, tags `curated`); the operation owns this table.
- Reads: [curated_mastersku.curated_product](/curated/curated_mastersku/curated_product.md), [validated_mastersku.product_detail](/validated/validated_mastersku/product_detail.md), [validated_mastersku.brand](/validated/validated_mastersku/brand.md), [validated_mastersku.category](/validated/validated_mastersku/category.md), [validated_mastersku.vendor](/validated/validated_mastersku/vendor.md), [validated_mastersku.unit](/validated/validated_mastersku/unit.md).
- Operations action (`type: "operations"`, tag `curated`; target table pre-exists in BigQuery, created outside this definition): builds a TEMP table, DELETEs `asatdate = run_date`, then INSERTs the new rows (not wrapped in a transaction). Runs after `curated_product`.

# Examples

Latest snapshot of the feed.

```sql
SELECT id, structData.product_name, structData.brand_name, structData.product_status
FROM `databuffet-nonprd.curated_mastersku.product_for_aisearch`
WHERE asatdate = (SELECT MAX(asatdate) FROM `databuffet-nonprd.curated_mastersku.product_for_aisearch`)
LIMIT 100
```

Duplicate SKUs in the latest snapshot.

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.curated_mastersku.product_for_aisearch`
WHERE asatdate = (SELECT MAX(asatdate) FROM `databuffet-nonprd.curated_mastersku.product_for_aisearch`)
GROUP BY id
HAVING n > 1
```

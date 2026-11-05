---
type: BigQuery Table
title: "product_detail"
description: "One row = one product detail record from source table `product_detail`, unique on (pd_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product_detail&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: product_detail
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product_detail.sqlx"
    title: "Dataform definition (validated/mastersku/product_detail.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MASTERSKU `product_detail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Extended attributes of each MASTERSKU product: name, series, model, material, sizes, package dimensions, weights with units, warranty, TIS certificate and usage texts.

Read by: [curated_mastersku.curated_product](/curated/curated_mastersku/curated_product.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md).

# Grain and key

One row per `pd_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `pd_id` | STRING | Unique identifier (UUID) of the product detail record. |
| `pd_prd_id` | STRING | Product this detail belongs to (FK to `product.prd_id`). |
| `pd_url_video` | STRING | URL of the product video. |
| `pd_detail` | STRING | Product description text (HTML). |
| `pd_series` | STRING | Product series name. |
| `pd_model` | STRING | Product model. |
| `pd_material` | STRING | Main material of the product (e.g. PE). |
| `pd_certificate` | STRING | Thai Industrial Standard (TIS) certificate of the product (e.g. `TIS.982-2556`). |
| `pd_garantee` | STRING | Warranty period of the product (e.g. `1Y`, `20 Y`). |
| `pd_garantee_detail` | STRING | Warranty terms and conditions text. |
| `pd_shape` | STRING | Packaging shape of the product (e.g. box, gallon, length). |
| `pd_supplier_country` | STRING | Country of the supplier (country of origin). |
| `pd_package_wide` | FLOAT64 | Package width. |
| `pd_package_long` | FLOAT64 | Package length. |
| `pd_package_hight` | FLOAT64 | Package height. |
| `pd_size_wide` | FLOAT64 | Product width. |
| `pd_size_long` | FLOAT64 | Product length (depth). |
| `pd_sl_id` | STRING | Unit of the product length `pd_size_long` (FK to `unit.unit_id`). |
| `pd_size_hight` | FLOAT64 | Product height. |
| `pd_sh_id` | STRING | Unit of the product height `pd_size_hight` (FK to `unit.unit_id`). |
| `pd_net_weight` | FLOAT64 | Net weight of the product. |
| `pd_gross_weight` | FLOAT64 | Gross (packed) weight of the product. |
| `pd_uw_id` | STRING | Unit of the package width `pd_package_wide` (FK to `unit.unit_id`). |
| `pd_ul_id` | STRING | Unit of the package length `pd_package_long` (FK to `unit.unit_id`). |
| `pd_uh_id` | STRING | Unit of the package height `pd_package_hight` (FK to `unit.unit_id`). |
| `pd_sw_id` | STRING | Unit of the product width `pd_size_wide` (FK to `unit.unit_id`). |
| `pd_net_unit_id` | STRING | Unit of the net weight (FK to `unit.unit_id`). |
| `pd_gross_unit_id` | STRING | Unit of the gross weight (FK to `unit.unit_id`). |
| `pd_how_to` | STRING | How-to-use text of the product (HTML). |
| `pd_how_to_url` | STRING | URL of the how-to-use document or media. |
| `pd_how_to_path` | STRING | Storage path of the how-to-use file. |
| `pd_suggest` | STRING | Usage recommendation text of the product (HTML). |
| `pd_suggest_url` | STRING | URL of the recommendation document or media. |
| `pd_suggest_path` | STRING | Storage path of the recommendation file. |
| `pd_caution` | STRING | Caution/warning text of the product (HTML). |
| `pd_caution_url` | STRING | URL of the caution document or media. |
| `pd_caution_path` | STRING | Storage path of the caution file. |
| `pd_file_name` | STRING | File name of the product image. |
| `pd_file_path` | STRING | Storage path of the product image file. |
| `pd_is_system` | BOOL | System flag of the product detail; TRUE together with the product active and in-use flags marks the product as approved. |
| `pd_created_date` | DATETIME | Timestamp when the record was created. |
| `pd_created_by` | STRING | Identifier of the user who created the record. |
| `pd_updated_date` | DATETIME | Timestamp when the record was last updated. |
| `pd_updated_by` | STRING | Identifier of the user who last updated the record. |
| `pd_product_name` | STRING | Full product name. |
| `pd_vendor_code` | STRING | Vendor own item code of the product. |
| `pd_barcode` | STRING | Barcode of the product. |
| `pd_sale_unit` | STRING | Sales unit of the product (e.g. `EA`). |
| `pd_spacific_fields` | STRING | Product-specific fields as JSON (`{"SpeciFeild":[{"label","value"}]}`). |
| `pd_remark_inactive` | STRING | Reason the product was made inactive (e.g. sale cancelled, duplicate). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product_detail.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product_detail](/initial/raw_mastersku/product_detail.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `pd_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product_detail`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT pd_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product_detail`
GROUP BY pd_id
HAVING n > 1
```

---
type: BigQuery View
title: "Product_Attribute"
description: "Current barcoded ag01 MAC5 stock joined to matching dim_product_master ProductSK rows and MASTERSKU attributes; a code can have multiple retained barcode versions."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=onetime&t=Product_Attribute&page=table"
project_id: databuffet-nonprd
dataset_id: onetime
table_id: Product_Attribute
tags: ["view", "onetime", "mac5", "mastersku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/onetime/Product_Attribute.sqlx"
    title: "Dataform definition (view/onetime/Product_Attribute.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Physical product attributes (colour, shape, weights, size, unit, material, model, series) for the products of company ag01. MAC5 stock items ([stk](/validated/validated_mac5/stk.md)) are linked by barcode to the MASTERSKU product master ([product](/validated/validated_mastersku/product.md), [product_detail](/validated/validated_mastersku/product_detail.md)), and the series name is mapped to [dim_product_series](/dimension/dim_product_series.md). It is a building block of the wide product view [Product_Master_ALL](/view/onetime/Product_Master_ALL.md).

Used by [onetime.Product_Master_ALL](/view/onetime/Product_Master_ALL.md).

# Grain and key

Each ag01 `stk` row with a non-empty `STKcode885` barcode joins every `dim_product_master` row with the same company and product code (`ProductSK IS NOT NULL`). The dimension key includes barcode, but this join omits it, so a code can emit multiple ProductSK rows for retained barcode versions. Joins to MASTERSKU are by barcode and could multiply rows if a barcode appears twice in `product`; the series join is guarded with an `OTHERS` fallback so it does not drop products.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductSK` | INT64 | SK of a matching `dim_product_master` row (stable MERGE dim). Matching uses company + `ProductCode`, without barcode; several retained barcode versions can produce different SKs for one code. |
| `CompanySK` | INT64 | SK of `dim_company` for ag01. |
| `SeriesSK` | INT64 | SK of `dim_product_series` for the product's series name; products whose series is missing or not in the dim fall to the `OTHERS` series. |
| `SeriesCode` | STRING | Code of that series (`dim_product_series.SeriesCode`). |
| `companyID` | STRING | Company code; always `ag01` (the view filters `company_id = 'ag01'`). |
| `ProductCode` | STRING | Product (stock item) code. |
| `ProductColor` | STRING | Color of the product. |
| `ProductShape` | STRING | Packaging shape of the product (e.g. box, gallon, length). |
| `ProductGrossWeight` | FLOAT64 | Gross (packed) weight of the product. |
| `ProductNetWeight` | FLOAT64 | Net weight of the product. |
| `ProductSeries` | STRING | Product series name. |
| `ProductSize` | STRING | Size of the product. |
| `ProductSizeHight` | FLOAT64 | Product height. |
| `ProductSizeLong` | FLOAT64 | Product length (depth). |
| `ProductSizeWide` | FLOAT64 | Product width. |
| `ProductUnit` | STRING | Sales unit of the product (e.g. `EA`). |
| `ProductMaterials` | STRING | Main material of the product (e.g. PE). |
| `ProductModel` | STRING | Product model. |

# How it is built

- Definition: `definitions/view/onetime/Product_Attribute.sqlx` (`type: "view"`, tags `view`).
- Reads: [validated_mac5.stk](/validated/validated_mac5/stk.md), [validated_mac5.stg](/validated/validated_mac5/stg.md), [validated_mastersku.product](/validated/validated_mastersku/product.md), [validated_mastersku.product_detail](/validated/validated_mastersku/product_detail.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_series](/dimension/dim_product_series.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `dim_company`, `dim_product_master` and `dim_product_series` (tag `dimension_daily`); `validated_mac5.stk/stg` and `validated_mastersku.product/product_detail` are read via `ref()`.

# Examples

Attributes of products in one series.

```sql
SELECT ProductCode, ProductColor, ProductSize, ProductUnit, ProductMaterials
FROM `databuffet-nonprd.onetime.Product_Attribute`
WHERE SeriesCode IS NOT NULL
ORDER BY ProductCode
LIMIT 100
```

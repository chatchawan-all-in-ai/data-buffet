---
type: BigQuery Table
title: "curated_products"
description: "One row = one product (master SKU) of the master_sku 3.0 catalogue, in the same 50-column layout as the old curated_product."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_master_sku&t=curated_products&page=table"
project_id: databuffet-nonprd
dataset_id: curated_master_sku
table_id: curated_products
tags: ["curated", "curated_master_sku", "master_sku", "MASTER_SKU"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/master_sku/curated_products.sqlx"
    title: "Dataform definition (curated/master_sku/curated_products.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Product catalogue built from the new master_sku source (validated_master_sku.products + brand_vendors + common_codes). It mirrors the 50 columns, names and order of [curated_product](/curated/curated_mastersku/curated_product.md); columns master_sku does not have are NULL. It is the master_sku counterpart of curated_product.

# Grain and key

One row per `prdSku` (= products.master_sku_code): placeholder rows without a master_sku_code are dropped and, if a code repeats, the row with the latest `updated_at` wins. No declared key because it is a rebuilt `table`.

# Schema

| Column | Type | Description |
|---|---|---|
| `prdId` | STRING | Unique identifier (UUID) of the product. |
| `prdSku` | STRING | Master SKU code of the product (`MSKU` + 10 digits). |
| `prdDescription` | STRING | Product name. |
| `prdD365Sku` | STRING | Item number of the product in Dynamics 365 (DERP). |
| `prdItemText` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdItemCode` | STRING | Item code of the product in the MAC5 ERP. |
| `prdStoppedSate` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent (the column name keeps the original typo) |
| `prdMadeToOrder` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdSaleUnite` | STRING | Sales unit name: common_codes.name of products.uom_sales_id; when that is the generic default 'ชิ้น' it is replaced by the unit in the trailing parentheses of the name (only if it is in the unit vocabulary), else by the first non-empty 'หน่วยขาย' variant value, else 'ชิ้น'. |
| `prdTag` | STRING | JSON text `{"mypro_tag":[...]}` built from products.tags (empty array when no tags; never NULL). |
| `prdUniversalBarcode` | STRING | Universal (GS1/EAN) barcode of the product. |
| `prdInternalBarcode` | STRING | Internal barcode/code assigned to the product. |
| `prdCatId` | STRING | Category of the product (FK to `categories.id`). |
| `prdFilter1` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdFilter2` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdBrandId` | STRING | Brand id (products.brand_id, else brand_vendors.brand_id for the products that only carry the brand on brand_vendors). These are master_sku ids, not the old mastersku ids; join to validated_master_sku.brands.id. |
| `prdSize` | STRING | Size: first non-empty variant value labelled 'ขนาด' or 'size' in products.specification_attributes, else d365_size with leading zeros removed (01000L becomes 1000L). |
| `prdLine` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdColorTH` | STRING | Thai part of the colour variant ('สี' / 'color' attribute): the leading Thai-character run, NULL when the colour starts with a non-Thai word. No fallback to color_descriptor_id. |
| `prdColorEN` | STRING | English part of the colour variant: the whole value when it does not start with Thai, otherwise the text after the leading Thai run. |
| `prdModel` | STRING | Model: COALESCE(products.model, variant 'โมเดล', variant 'รุ่นสินค้า'). |
| `prdDimension1` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDimension2` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDimension3` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDimension4` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdVendorId` | STRING | Vendor that supplies the brand (FK to `vendors.id`). |
| `prdIsActive` | BOOL | TRUE when products.product_status = 'Active'. |
| `prdIsUse` | BOOL | TRUE when products.sales_status = 'Active'. |
| `prdCreatedDate` | DATETIME | Timestamp when the record was created. |
| `prdCreatedBy` | STRING | Identifier of the user who created the record. |
| `prdUpdatedDate` | DATETIME | products.updated_at, but when it is the 2000-01-01 placeholder (< 2000-01-02) the first non-null of product_status_date, sales_status_date, updated_at is used. |
| `prdUpdatedBy` | STRING | Identifier of the user who last updated the record. |
| `prdPgId` | STRING | Specification group (product family) of the product (FK to `spec_groups.id`); equals the old MASTERSKU product group id. |
| `prdPsId` | STRING | Constant id of the old product-status lookup: 5430ac8c-... (On) when product_status = 'Active', else 7f5ac89b-... (Off). |
| `prdIdSource` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdMcId` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDiminsionData` | STRING | JSON text `{"dimFeild":[{"label":..., "value":...}]}` built from products.specification_attributes in array order (the column name and the keys keep the source typos on purpose). |
| `prdPasId` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdBarcode` | STRING | Universal (GS1/EAN) barcode of the product. |
| `prdRejectRemark` | STRING | Remark on the latest product status change (e.g. rejection reason). |
| `prdRefMpId` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdIsCombo` | BOOL | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdComboPrice` | FLOAT64 | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdIsTime` | BOOL | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdComboStart` | DATETIME | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdComboEnd` | DATETIME | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdTotalComboPrice` | FLOAT64 | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdTotalCostComboPrice` | FLOAT64 | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdBarcodeFormat` | STRING | Barcode format name from common_codes (universal_barcode_format_id); 'EAN13' is renamed to 'GTIN-13 / EAN-13' to match the old catalogue. |
| `asatdate` | DATE | products.asatdate of the selected product row; partition column. |

# How it is built

- Definition: `definitions/curated/master_sku/curated_products.sqlx` (`type: "table"`, tags `curated`).
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["prdSku", "prdUniversalBarcode", "prdVendorId", "prdBrandId"]}`.
- Reads: [validated_master_sku.products](/validated/validated_master_sku/products.md), [validated_master_sku.common_codes](/validated/validated_master_sku/common_codes.md), [validated_master_sku.brand_vendors](/validated/validated_master_sku/brand_vendors.md).
- Full daily rebuild (`type: "table"`, tag `curated`, after `curated_schema_master_sku` and `validated_master_sku.products`, `brand_vendors`, `common_codes`); partitioned by `asatdate`, clustered by prdSku, prdUniversalBarcode, prdVendorId, prdBrandId.

# Examples

One product by SKU.

```sql
SELECT prdSku, prdDescription, prdBrandId, prdVendorId, prdSize, prdColorTH, prdColorEN, prdIsActive, prdIsUse
FROM `databuffet-nonprd.curated_master_sku.curated_products`
WHERE prdSku = 'REPLACE_WITH_SKU'
```

Active, sellable product counts per brand id.

```sql
SELECT prdBrandId, COUNT(*) AS n
FROM `databuffet-nonprd.curated_master_sku.curated_products`
WHERE prdIsActive AND prdIsUse
GROUP BY prdBrandId
ORDER BY n DESC
LIMIT 20
```

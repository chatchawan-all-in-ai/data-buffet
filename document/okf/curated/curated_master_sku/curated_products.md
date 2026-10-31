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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Product catalogue built from the new master_sku source (validated_master_sku.products + brand_vendors + common_codes). It deliberately mirrors the 50 columns, names and order of [curated_product](/curated/curated_mastersku/curated_product.md) so consumers can switch source; columns master_sku does not have are NULL. No other object in the repo reads it yet (consumers are external, e.g. AI search / reporting); it is the master_sku counterpart of the older MASTERSKU table.

# Grain and key

One row per `prdSku` (= products.master_sku_code): placeholder rows without a master_sku_code are dropped and, if a code repeats, the row with the latest `updated_at` wins. No declared key because it is a rebuilt `table`.

# Schema

| Column | Type | Description |
|---|---|---|
| `prdId` | STRING | Product row id (products.id, a UUID-like string) from validated_master_sku.products. |
| `prdSku` | STRING | Master SKU code (products.master_sku_code); the business key, one row per value. |
| `prdDescription` | STRING | Product name (products.name); for master_sku the name often ends with the old free-text sales unit in parentheses. |
| `prdD365Sku` | STRING | Dynamics 365 item code (products.d365_code). |
| `prdItemText` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdItemCode` | STRING | MAC5 item code (products.mac5_code); link to MAC5 stock codes. |
| `prdStoppedSate` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent (the column name keeps the original typo) |
| `prdMadeToOrder` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdSaleUnite` | STRING | Sales unit name: common_codes.name of products.uom_sales_id; when that is the generic default 'ชิ้น' it is replaced by the unit in the trailing parentheses of the name (only if it is in the unit vocabulary), else by the first non-empty 'หน่วยขาย' variant value, else 'ชิ้น'. |
| `prdTag` | STRING | JSON text `{"mypro_tag":[...]}` built from products.tags (empty array when no tags; never NULL). |
| `prdUniversalBarcode` | STRING | Universal barcode (products.universal_barcode, e.g. EAN13); also a cluster column. |
| `prdInternalBarcode` | STRING | Internal barcode (products.internal_barcode). |
| `prdCatId` | STRING | Category id (products.category_id); join to validated_master_sku.categories.id. |
| `prdFilter1` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdFilter2` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdBrandId` | STRING | Brand id (products.brand_id, else brand_vendors.brand_id for the 52 products that only carry the brand on brand_vendors). These are master_sku ids, not the old mastersku ids; join to validated_master_sku.brands.id. |
| `prdSize` | STRING | Size: first non-empty variant value labelled 'ขนาด' or 'size' in products.specification_attributes, else d365_size with leading zeros removed (01000L becomes 1000L). |
| `prdLine` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdColorTH` | STRING | Thai part of the colour variant ('สี' / 'color' attribute): the leading Thai-character run, NULL when the colour starts with a non-Thai word. No fallback to color_descriptor_id. |
| `prdColorEN` | STRING | English part of the colour variant: the whole value when it does not start with Thai, otherwise the text after the leading Thai run. |
| `prdModel` | STRING | Model: COALESCE(products.model, variant 'โมเดล', variant 'รุ่นสินค้า'). |
| `prdDimension1` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDimension2` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDimension3` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDimension4` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdVendorId` | STRING | Vendor id taken from brand_vendors (products has no vendor_id); join to validated_master_sku.vendors.id; cluster column. |
| `prdIsActive` | BOOL | TRUE when products.product_status = 'Active'. |
| `prdIsUse` | BOOL | TRUE when products.sales_status = 'Active'. |
| `prdCreatedDate` | DATETIME | products.created_at (about 26k placeholder rows without master_sku_code carry 2000-01-01 and are excluded). |
| `prdCreatedBy` | STRING | products.created_by. |
| `prdUpdatedDate` | DATETIME | products.updated_at, but when it is the 2000-01-01 placeholder (< 2000-01-02) the first non-null of product_status_date, sales_status_date, updated_at is used. |
| `prdUpdatedBy` | STRING | products.updated_by. |
| `prdPgId` | STRING | products.specification_group_id (matches the old product-group id; product_group_id does not). |
| `prdPsId` | STRING | Constant id of the old product-status lookup: 5430ac8c-... (On) when product_status = 'Active', else 7f5ac89b-... (Off). |
| `prdIdSource` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdMcId` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdDiminsionData` | STRING | JSON text `{"dimFeild":[{"label":..., "value":...}]}` built from products.specification_attributes in array order (the column name and the keys keep the source typos on purpose). |
| `prdPasId` | STRING | Always NULL: the column is kept for compatibility with the old catalogue layout and master_sku has no equivalent |
| `prdBarcode` | STRING | Same as prdUniversalBarcode (products.universal_barcode). |
| `prdRejectRemark` | STRING | products.product_status_remark. |
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
- Approximate size (BigQuery metadata, 2026-10-31): 103,206 rows, 78.3 MB.

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

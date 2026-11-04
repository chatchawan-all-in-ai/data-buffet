---
type: BigQuery Table
title: "curated_product"
description: "One row = one product SKU of the legacy MASTERSKU catalogue, unique on prdSku (latest prdUpdatedDate wins)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mastersku&t=curated_product&page=table"
project_id: databuffet-nonprd
dataset_id: curated_mastersku
table_id: curated_product
tags: ["curated", "curated_mastersku", "mastersku", "MASTERSKU"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/mastersku/curated_product.sqlx"
    title: "Dataform definition (curated/mastersku/curated_product.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Product catalogue of the legacy MASTERSKU source: a camelCase rename of validated_mastersku.product with colour and size re-derived from the product JSON (post-operation). It is the input of [product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md) (the AI-search feed). The master_sku 3.0 successor with the same 50 columns is [curated_products](/curated/curated_master_sku/curated_products.md).

# Grain and key

One row per `prdSku` (the MERGE `uniqueKey`); dedup is `ROW_NUMBER() OVER (PARTITION BY prdSku ORDER BY prdUpdatedDate DESC) = 1`. `prdId` links to product_detail.

# Schema

| Column | Type | Description |
|---|---|---|
| `prdId` | STRING | Unique identifier (UUID) of the product. |
| `prdSku` | STRING | Master SKU code of the product (`MSKU` + 10 digits). |
| `prdDescription` | STRING | Product name/description. |
| `prdD365Sku` | STRING | Item number of the product in Dynamics 365. |
| `prdItemText` | STRING | Free-text item text of the product. |
| `prdItemCode` | STRING | Item code of the product in the MAC5 ERP. |
| `prdStoppedSate` | STRING | Date the product was stopped (discontinued). |
| `prdMadeToOrder` | STRING | Made-to-order indicator of the product. |
| `prdSaleUnite` | STRING | Sales unit of the product (e.g. `EA`, `SET`, `ชุด`, `ชิ้น`). |
| `prdTag` | STRING | Search tags of the product as JSON (`{"mypro_tag":[...]}`). |
| `prdUniversalBarcode` | STRING | Universal (GS1/EAN) barcode of the product. |
| `prdInternalBarcode` | STRING | Internal barcode/code assigned to the product. |
| `prdCatId` | STRING | Category of the product (FK to `category.cat_id`). |
| `prdFilter1` | STRING | First search filter value of the product. |
| `prdFilter2` | STRING | Second search filter value of the product. |
| `prdBrandId` | STRING | Brand of the product (FK to `brand.bra_id`). |
| `prdSize` | STRING | Size: pass-through of prd_size, then overwritten by the post-operation with the 'ขนาด'/'size' value from the product JSON (dimFeild first, then SpeciFeild from product_detail.pd_spacific_fields). |
| `prdLine` | STRING | Product line. |
| `prdColorTH` | STRING | Thai part of the colour: set by the post-operation UPDATE from the 'สี'/'color' label in the product JSON (leading Thai-character run); NULL when the colour starts with a non-Thai word. |
| `prdColorEN` | STRING | English part of the colour: set by the post-operation UPDATE (whole value if it does not start with Thai, else the text after the Thai run). Both colour columns start as prd_color. |
| `prdModel` | STRING | Model of the product. |
| `prdDimension1` | STRING | Value of variant dimension 1 of the product (label set by its product group `pg_dimension1`). |
| `prdDimension2` | STRING | Value of variant dimension 2 of the product (label set by its product group `pg_dimension2`). |
| `prdDimension3` | STRING | Value of variant dimension 3 of the product (label set by its product group `pg_dimension3`). |
| `prdDimension4` | STRING | Value of variant dimension 4 of the product (label set by its product group `pg_dimension4`). |
| `prdVendorId` | STRING | Vendor (supplier) of the product (FK to `vendor.vd_id`). |
| `prdIsActive` | BOOL | Product active flag (product status is active). |
| `prdIsUse` | BOOL | Product open-for-sale flag. |
| `prdCreatedDate` | DATETIME | Timestamp when the record was created. |
| `prdCreatedBy` | STRING | Identifier of the user who created the record. |
| `prdUpdatedDate` | DATETIME | Timestamp when the record was last updated. |
| `prdUpdatedBy` | STRING | Identifier of the user who last updated the record. |
| `prdPgId` | STRING | Product group of the product (FK to `product_group.pg_id`). |
| `prdPsId` | STRING | Product status (FK to `product_status.ps_id`; e.g. On, Off, Draft, Pending, Approve, Reject). |
| `prdIdSource` | STRING | Product identifier in the system the product was imported from (barcode-like code). |
| `prdMcId` | STRING | Merchandise category identifier of the product. |
| `prdDiminsionData` | STRING | Variant dimension labels and values as JSON (`{"dimFeild":[{"label","value"}]}`). |
| `prdPasId` | STRING | Admin review status of the product (FK to `product_admin_status.pas_id`; e.g. new, edit, duplicate, open, close, delete). |
| `prdBarcode` | STRING | Barcode of the product, used to match MAC5 products (`STKcode885`). |
| `prdRejectRemark` | STRING | Remark explaining why the product was rejected. |
| `prdRefMpId` | STRING | Reference to the master product record this product was created from. |
| `prdIsCombo` | BOOL | Flag marking the product as a combo (bundle) set. |
| `prdComboPrice` | FLOAT64 | Selling price of the combo set. |
| `prdIsTime` | BOOL | Flag marking the combo as time-limited (valid between `prd_combo_start` and `prd_combo_end`). |
| `prdComboStart` | DATETIME | Start date-time of the combo offer. |
| `prdComboEnd` | DATETIME | End date-time of the combo offer. |
| `prdTotalComboPrice` | FLOAT64 | Total selling price of all items in the combo. |
| `prdTotalCostComboPrice` | FLOAT64 | Total cost price of all items in the combo. |
| `prdBarcodeFormat` | STRING | Barcode format of the product (e.g. `GTIN-13 / EAN-13`, `GTIN-12 / UPC-A`). |
| `asatdate` | DATE | Extract date of the validated row; partition column and the incremental window column. |

# How it is built

- Definition: `definitions/curated/mastersku/curated_product.sqlx` (`type: "incremental"`, tags `curated`).
- `uniqueKey`: `prdSku`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["prdSku", "prdUniversalBarcode", "prdVendorId", "prdBrandId"], "updatePartitionFilter": "asatdate >= CURRENT_DATE('Asia/Bangkok')-7"}`.
- Reads: [validated_mastersku.product](/validated/validated_mastersku/product.md), [validated_mastersku.product_detail](/validated/validated_mastersku/product_detail.md).
- Incremental MERGE on `prdSku` (tag `curated`; no dependency declared beyond ref() to `validated_mastersku.product`); reads only the last `BACKFILL_DAYS` day(s) of validated rows; `updatePartitionFilter` limits the MERGE to the last 7 days of partitions. A `post_operations` UPDATE then fills `prdColorTH`, `prdColorEN`, `prdSize` for the same window from `product_detail` and the JSON in `prdDiminsionData` (`$.dimFeild`) and `pd_spacific_fields` (`$.SpeciFeild`).

# Examples

One SKU with its derived size and colours.

```sql
SELECT prdSku, prdDescription, prdSize, prdColorTH, prdColorEN, prdBrandId, prdVendorId, prdIsActive
FROM `databuffet-nonprd.curated_mastersku.curated_product`
WHERE prdSku = 'REPLACE_WITH_SKU'
ORDER BY prdUpdatedDate DESC
LIMIT 1
```

Duplicate SKUs (the MERGE window can create them).

```sql
SELECT prdSku, COUNT(*) AS n
FROM `databuffet-nonprd.curated_mastersku.curated_product`
GROUP BY prdSku
HAVING n > 1
```

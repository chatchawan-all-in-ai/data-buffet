---
type: BigQuery Table
title: "curated_product"
description: "One row = one product SKU of the legacy MASTERSKU catalogue, unique on prdSku (latest prdUpdatedDate wins)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mastersku&t=curated_product&page=table"
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
| `prdId` | STRING | Product row id (prd_id) from validated_mastersku.product; also the join key to product_detail.pd_prd_id. |
| `prdSku` | STRING | Product SKU (prd_sku); the MERGE key (one row per prdSku, latest prdUpdatedDate wins). |
| `prdDescription` | STRING | Product description / name (prd_description). |
| `prdD365Sku` | STRING | Pass-through of prd_d365_sku. |
| `prdItemText` | STRING | Pass-through of prd_item_text. |
| `prdItemCode` | STRING | Pass-through of prd_item_code. |
| `prdStoppedSate` | STRING | Pass-through of prd_stopped_sate (source typo kept). |
| `prdMadeToOrder` | STRING | Pass-through of prd_made_to_order. |
| `prdSaleUnite` | STRING | Pass-through of prd_sale_unite (sales unit). |
| `prdTag` | STRING | Pass-through of prd_tag. |
| `prdUniversalBarcode` | STRING | Pass-through of prd_universal_barcode; cluster column. |
| `prdInternalBarcode` | STRING | Pass-through of prd_internal_barcode. |
| `prdCatId` | STRING | Pass-through of prd_cat_id (category id; join to validated_mastersku.category.cat_id). |
| `prdFilter1` | STRING | Pass-through of prd_filter1. |
| `prdFilter2` | STRING | Pass-through of prd_filter2. |
| `prdBrandId` | STRING | Pass-through of prd_brand_id (join to validated_mastersku.brand.bra_id). |
| `prdSize` | STRING | Size: pass-through of prd_size, then overwritten by the post-operation with the 'ขนาด'/'size' value from the product JSON (dimFeild first, then SpeciFeild from product_detail.pd_spacific_fields). |
| `prdLine` | STRING | Pass-through of prd_line. |
| `prdColorTH` | STRING | Thai part of the colour: set by the post-operation UPDATE from the 'สี'/'color' label in the product JSON (leading Thai-character run); NULL when the colour starts with a non-Thai word. |
| `prdColorEN` | STRING | English part of the colour: set by the post-operation UPDATE (whole value if it does not start with Thai, else the text after the Thai run). Both colour columns start as prd_color. |
| `prdModel` | STRING | Pass-through of prd_model. |
| `prdDimension1` | STRING | Pass-through of prd_dimension1. |
| `prdDimension2` | STRING | Pass-through of prd_dimension2. |
| `prdDimension3` | STRING | Pass-through of prd_dimension3. |
| `prdDimension4` | STRING | Pass-through of prd_dimension4. |
| `prdVendorId` | STRING | Pass-through of prd_vendor_id (join to validated_mastersku.vendor.vd_id); cluster column. |
| `prdIsActive` | BOOL | Pass-through of prd_is_active. |
| `prdIsUse` | BOOL | Pass-through of prd_is_use. |
| `prdCreatedDate` | DATETIME | Pass-through of prd_created_date. |
| `prdCreatedBy` | STRING | Pass-through of prd_created_by. |
| `prdUpdatedDate` | DATETIME | Pass-through of prd_updated_date; the dedup order (latest wins). |
| `prdUpdatedBy` | STRING | Pass-through of prd_updated_by. |
| `prdPgId` | STRING | Pass-through of prd_pg_id. |
| `prdPsId` | STRING | Pass-through of prd_ps_id. |
| `prdIdSource` | STRING | Pass-through of prd_id_source. |
| `prdMcId` | STRING | Pass-through of prd_mc_id. |
| `prdDiminsionData` | STRING | Pass-through of prd_diminsion_data: JSON text with a `dimFeild` array of label/value pairs (source typos are load-bearing). |
| `prdPasId` | STRING | Pass-through of prd_pas_id. |
| `prdBarcode` | STRING | Pass-through of prd_barcode. |
| `prdRejectRemark` | STRING | Pass-through of prd_reject_remark. |
| `prdRefMpId` | STRING | Pass-through of prd_ref_mp_id. |
| `prdIsCombo` | BOOL | Pass-through of prd_is_combo. |
| `prdComboPrice` | FLOAT64 | Pass-through of prd_combo_price. |
| `prdIsTime` | BOOL | Pass-through of prd_is_time. |
| `prdComboStart` | DATETIME | Pass-through of prd_combo_start. |
| `prdComboEnd` | DATETIME | Pass-through of prd_combo_end. |
| `prdTotalComboPrice` | FLOAT64 | Pass-through of prd_total_combo_price. |
| `prdTotalCostComboPrice` | FLOAT64 | Pass-through of prd_total_cost_combo_price. |
| `prdBarcodeFormat` | STRING | Pass-through of prd_barcode_format. |
| `asatdate` | DATE | Extract date of the validated row; partition column and the incremental window column. |

# How it is built

- Definition: `definitions/curated/mastersku/curated_product.sqlx` (`type: "incremental"`, tags `curated`).
- `uniqueKey`: `prdSku`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["prdSku", "prdUniversalBarcode", "prdVendorId", "prdBrandId"], "updatePartitionFilter": "asatdate >= CURRENT_DATE('Asia/Bangkok')-7"}`.
- Reads: [validated_mastersku.product](/validated/validated_mastersku/product.md), [validated_mastersku.product_detail](/validated/validated_mastersku/product_detail.md).
- Incremental MERGE on `prdSku` (tag `curated`; no dependency declared beyond ref() to `validated_mastersku.product`); reads only the last `BACKFILL_DAYS` day(s) of validated rows; `updatePartitionFilter` limits the MERGE to the last 7 days of partitions. A `post_operations` UPDATE then fills `prdColorTH`, `prdColorEN`, `prdSize` for the same window from `product_detail` and the JSON in `prdDiminsionData` (`$.dimFeild`) and `pd_spacific_fields` (`$.SpeciFeild`).
- Approximate size (BigQuery metadata, 2026-10-31): 110,121 rows, 93.3 MB.

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

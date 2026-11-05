---
type: BigQuery View
title: "Product_Master_ALL"
description: "An ag01 dim_product_master barcode version enriched with descriptions, marketing hierarchy, marketing director and physical attributes."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=onetime&t=Product_Master_ALL&page=table"
project_id: databuffet-nonprd
dataset_id: onetime
table_id: Product_Master_ALL
tags: ["view", "onetime"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/onetime/Product_Master_ALL.sqlx"
    title: "Dataform definition (view/onetime/Product_Master_ALL.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The wide product master: [dim_product_master](/dimension/dim_product_master.md) (MAC5 + MASTERSKU descriptions, warranty, TIS flag, barcode) joined to the marketing hierarchy ([view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md): group, sub group, segment, type), the marketing director ([dim_product_mkt_director](/dimension/dim_product_mkt_director.md)) and the physical attributes of [Product_Attribute](/view/onetime/Product_Attribute.md). It carries no SKs.

No other object in this repo reads it.

# Grain and key

One row = one `dim_product_master` row of company `ag01` with each combination of joined matches: intended key `ProductCode`, `Barcode` (not unique). The source key also includes `CompanySK` (constant for this company and not exposed by this view), with NULL barcode matched as empty. [view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md) is joined on `ProductMktSK` + `CompanySK`, [Product_Attribute](/view/onetime/Product_Attribute.md) on `ProductSK` + `CompanySK` (can return several rows per `ProductSK`), and `dim_product_mkt_director` on `ProductMktDirectorSK` + `CompanySK`; all are LEFT JOINs.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductCode` | STRING | MAC5 stock code (`dim_product_master.ProductCode`). |
| `ProductCode1` | STRING | Secondary product code or short model name. |
| `ProductMac5Description` | STRING | MAC5 Thai product description (`stk.stkdesct1`). |
| `ProductGroupMAC5` | STRING | Stock group code. |
| `ProductGroupMac5Description` | STRING | Thai name of the stock group. |
| `ProductGroupMAC5Type` | STRING | English name or type label of the stock group. |
| `ProductGroupACC` | STRING | Accounting product group code of the stock group (from `stgacc`). |
| `ProductGroupACCName` | STRING | Accounting product group name of the stock group (from `stgacc`). |
| `ProductName` | STRING | Full product name. |
| `ProductDescription` | STRING | Product name/description. |
| `ProductDimension1` | STRING | Value of variant dimension 1 of the product (label set by its product group `pg_dimension1`). |
| `ProductDimension2` | STRING | Value of variant dimension 2 of the product (label set by its product group `pg_dimension2`). |
| `ProductDimension3` | STRING | Value of variant dimension 3 of the product (label set by its product group `pg_dimension3`). |
| `ProductDimension4` | STRING | Value of variant dimension 4 of the product (label set by its product group `pg_dimension4`). |
| `ProductGarantee` | STRING | Warranty period of the product (e.g. `1Y`, `20 Y`). |
| `ProductGaranteeDetail` | STRING | Warranty terms and conditions text. |
| `ThaiIndustrialStandardFlag` | STRING | `Yes` when `pd_certificate` is filled with a real value (not empty, `โปรดระบุ`, `-`, `None`, `No`), else `No` (TIS certification flag). |
| `ThaiIndustrialSatandardDetail` | STRING | Thai Industrial Standard (TIS) certificate of the product (e.g. `TIS.982-2556`). |
| `Barcode` | STRING | Barcode (`stk.stkcode885`). |
| `MarketingGroupID` | STRING | Marketing group id from `view_dim_product_mkt` (via ProductMktSK). |
| `MarketingGroup` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing group id. |
| `SubMarketing` | STRING | Sub-marketing group name. |
| `SegmentID` | STRING | Segment id. |
| `Segment` | STRING | Segment name. |
| `TypeMarketingID` | STRING | Marketing type id. |
| `TypeMarketing` | STRING | Marketing type name. |
| `DirectorMarketingName` | STRING | First name of the marketing director responsible for the marketing type (`dim_product_mkt_director.name`). |
| `DirectorMarketingSurname` | STRING | Surname of that director. |
| `DirectorMarketingNameSurname` | STRING | Name and surname concatenated. |
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

- Definition: `definitions/view/onetime/Product_Master_ALL.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_view.view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [dimension_table.dim_product_mkt_director](/dimension/dim_product_mkt_director.md).

# Examples

Products by marketing group with their barcode.

```sql
SELECT MarketingGroupID, MarketingGroup, SubMarketing, Segment, ProductCode, ProductMac5Description, Barcode
FROM `databuffet-nonprd.onetime.Product_Master_ALL`
WHERE MarketingGroupID IS NOT NULL
ORDER BY MarketingGroupID, ProductCode
LIMIT 200
```

Count of view rows with and without a Thai Industrial Standard certificate.

```sql
SELECT ThaiIndustrialStandardFlag, COUNT(*) AS products
FROM `databuffet-nonprd.onetime.Product_Master_ALL`
GROUP BY ThaiIndustrialStandardFlag
```

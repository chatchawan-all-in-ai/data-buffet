---
type: BigQuery View
title: "Product_Master_ALL"
description: "An ag01 dim_product_master barcode version enriched with descriptions, marketing hierarchy, marketing director and physical attributes; enrichment joins can multiply rows."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=onetime&t=Product_Master_ALL&page=table"
tags: ["view", "onetime"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/onetime/Product_Master_ALL.sqlx"
    title: "Dataform definition (view/onetime/Product_Master_ALL.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The one-stop product master for BI: [dim_product_master](/dimension/dim_product_master.md) (MAC5 + MASTERSKU descriptions, warranty, TIS flag, barcode) joined to the marketing hierarchy ([view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md): group, sub group, segment, type), the marketing director ([dim_product_mkt_director](/dimension/dim_product_mkt_director.md)) and the physical attributes of [Product_Attribute](/view/onetime/Product_Attribute.md). It carries no SKs.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

Starts from each `dim_product_master` row of company `ag01`, whose natural key is (`CompanySK`, `ProductCode`, `Barcode`), with NULL barcode matched as empty. A barcode change leaves the old row, so `ProductCode` alone is not unique. Marketing, attributes and director are LEFT JOINed on SK + CompanySK; duplicate matches in those inputs can multiply rows further.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductCode` | STRING | MAC5 stock code (`dim_product_master.ProductCode`). |
| `ProductCode1` | STRING | Alternative MAC5 stock code (`stk.stkcode2`). |
| `ProductMac5Description` | STRING | MAC5 Thai product description (`stk.stkdesct1`). |
| `ProductGroupMAC5` | STRING | MAC5 stock group code (`stg.stgcode`). |
| `ProductGroupMac5Description` | STRING | Thai stock group description (`stg.stgdesct`). |
| `ProductGroupMAC5Type` | STRING | English description/type of the stock group (`stg.stgdesce`). |
| `ProductGroupACC` | STRING | Accounting group code (`stg.gacccode`). |
| `ProductGroupACCName` | STRING | Accounting group name (`stg.gaccname`). |
| `ProductName` | STRING | Product name from MASTERSKU (`product_detail.pd_product_name`). |
| `ProductDescription` | STRING | Description from MASTERSKU (`product.prd_description`). |
| `ProductDimension1` | STRING | MASTERSKU `prd_dimension1`; meaning not documented in the repo. |
| `ProductDimension2` | STRING | MASTERSKU `prd_dimension2`; meaning not documented in the repo. |
| `ProductDimension3` | STRING | MASTERSKU `prd_dimension3`; meaning not documented in the repo. |
| `ProductDimension4` | STRING | MASTERSKU `prd_dimension4`; meaning not documented in the repo. |
| `ProductGarantee` | STRING | Warranty text (`product_detail.pd_garantee`; spelling follows the source). |
| `ProductGaranteeDetail` | STRING | Warranty detail (`pd_garantee_detail`). |
| `ThaiIndustrialStandardFlag` | STRING | `Yes` when `pd_certificate` is filled with a real value (not empty, `โปรดระบุ`, `-`, `None`, `No`), else `No` (TIS certification flag). |
| `ThaiIndustrialSatandardDetail` | STRING | Certificate text (`pd_certificate`); the typo `Satandard` is the real column name. |
| `Barcode` | STRING | Barcode (`stk.stkcode885`). |
| `MarketingGroupID` | STRING | Marketing group id from `view_dim_product_mkt` (via ProductMktSK). |
| `MarketingGroup` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing group id. |
| `SubMarketing` | STRING | Sub-marketing group name. |
| `SegmentID` | STRING | Segment id. |
| `Segment` | STRING | Segment name. |
| `TypeMarketingID` | STRING | Marketing type id. |
| `TypeMarketing` | STRING | Marketing type name. |
| `DirectorMarketingName` | STRING | First name of the marketing director responsible for the marketing type (`dim_product_mkt_director.name`, personal data). |
| `DirectorMarketingSurname` | STRING | Surname of that director (personal data). |
| `DirectorMarketingNameSurname` | STRING | Name and surname concatenated (personal data). |
| `ProductColor` | STRING | Colour from `Product_Attribute`. |
| `ProductShape` | STRING | Shape from `Product_Attribute`. |
| `ProductGrossWeight` | FLOAT64 | Gross weight from `Product_Attribute`. |
| `ProductNetWeight` | FLOAT64 | Net weight from `Product_Attribute`. |
| `ProductSeries` | STRING | Series text from `Product_Attribute`. |
| `ProductSize` | STRING | Size text from `Product_Attribute`. |
| `ProductSizeHight` | FLOAT64 | Height from `Product_Attribute` (typo is the real name). |
| `ProductSizeLong` | FLOAT64 | Length from `Product_Attribute`. |
| `ProductSizeWide` | FLOAT64 | Width from `Product_Attribute`. |
| `ProductUnit` | STRING | Sale unit from `Product_Attribute`. |
| `ProductMaterials` | STRING | Material from `Product_Attribute`. |
| `ProductModel` | STRING | Model from `Product_Attribute`. |

# How it is built

- Definition: `definitions/view/onetime/Product_Master_ALL.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_view.view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [dimension_table.dim_product_mkt_director](/dimension/dim_product_mkt_director.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `dim_product_master`, `view_dim_product_mkt`, `Product_Attribute` (a view in `onetime`) and `dim_product_mkt_director`; the base dims are rebuilt in `dimension_daily`.

# Examples

Products by marketing group with their barcode.

```sql
SELECT MarketingGroupID, MarketingGroup, SubMarketing, Segment, ProductCode, ProductMac5Description, Barcode
FROM `databuffet-nonprd.onetime.Product_Master_ALL`
WHERE MarketingGroupID IS NOT NULL
ORDER BY MarketingGroupID, ProductCode
LIMIT 200
```

Count of view rows with and without a Thai Industrial Standard certificate (retained barcode versions and enrichment duplicates count separately).

```sql
SELECT ThaiIndustrialStandardFlag, COUNT(*) AS products
FROM `databuffet-nonprd.onetime.Product_Master_ALL`
GROUP BY ThaiIndustrialStandardFlag
```

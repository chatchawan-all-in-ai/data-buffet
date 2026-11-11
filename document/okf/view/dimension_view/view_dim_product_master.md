---
type: BigQuery View
title: "view_dim_product_master"
description: "One row = one product (`ProductSK`) from dim_product_master with rebate exclusion flags (`FlagSalesExc`, `FlagAccExc`) and the pump segment (`PumpSegment`)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_product_master&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_product_master
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_product_master.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_product_master.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-11T18:33:42+07:00" }
status: draft
---

# What it is

Product dimension for BI: [dim_product_master](/dimension/dim_product_master.md) (MAC5 stock + MASTERSKU product attributes) plus `FlagSalesExc`/`FlagAccExc` (from [dim_rebate](/dimension/dim_rebate.md), status 'Product') and `PumpSegment` (derived from the marketing segment and the WaterPac code parsed from the product code). The WaterPac name comes from [dim_waterpac](/dimension/dim_waterpac.md).

Read by: [dim_pump_information](/dimension/dim_pump_information.md) and [export_view_dim_product_master](/view/pub_sub/export_view_dim_product_master.md).

# Grain and key

One row = one dim_product_master row: key `ProductSK`; the source grain is owned by the [product card](/dimension/dim_product_master.md#grain-and-key). The three dim_waterpac joins are on `CompanySK` + upper-case WaterPac code and add no rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductSK` | INT64 | SK of the product in dim_product_master (MERGE). |
| `StkMktSK` | INT64 | SK of the stock-marketing mapping in dim_stk_mkt. |
| `ProductMktSK` | INT64 | SK of the marketing classification in dim_product_mkt. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `ProductCode` | STRING | MAC5 stock code (`stkcode`). |
| `ProductCode1` | STRING | Secondary product code or short model name. |
| `ProductMac5Description` | STRING | MAC5 stock description (`stkdesct1`). |
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
| `ThaiIndustrialStandardFlag` | STRING | `Yes` when the product has a Thai Industrial Standard (TIS) certificate in `product_detail.pd_certificate` (not empty, `-`, `No`, `None` or `โปรดระบุ`), else `No`. |
| `ThaiIndustrialSatandardDetail` | STRING | Thai Industrial Standard (TIS) certificate of the product (e.g. `TIS.982-2556`). |
| `BrandID` | STRING | Brand of the product (FK to `brand.bra_id`). |
| `VendorID` | STRING | Vendor (supplier) of the product (FK to `vendor.vd_id`). |
| `WarehouseID` | STRING | Default warehouse code of the item (joins `sto.stocode`). |
| `Barcode` | STRING | Barcode (`STKcode885`). |
| `FlagSalesExc` | STRING | `salesExc` from dim_rebate (status 'Product') matched on ProductCode and CompanySK; 'No' when none. |
| `FlagAccExc` | STRING | `accExc` from dim_rebate (status 'Product'); 'No' when none. |
| `PumpSegment` | STRING | Pump segment label: for SegmentID 00111/00112 the WaterPac name, taken as the first non-NULL of the dim_waterpac names matched by the WaterPac code of `ProductCode`, `ProductCode1`, `ProductMac5Description` (in that order), else 'WaterPac'; the marketing Segment for MarketingGroupID 002; else 'OTHERS'. The WaterPac code is the text after `/` that starts with P or U (regex `/([PU][a-zA-Z0-9].*)$`). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_product_master.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_rebate](/dimension/dim_rebate.md), [dimension_table.dim_waterpac](/dimension/dim_waterpac.md).

# Examples

Pump products by pump segment:

```sql
SELECT PumpSegment, COUNT(*) AS products
FROM `databuffet-nonprd.dimension_view.view_dim_product_master`
WHERE companyID = 'ag01'
GROUP BY PumpSegment
ORDER BY products DESC
```

Products excluded from sales rebate:

```sql
SELECT ProductCode, ProductName
FROM `databuffet-nonprd.dimension_view.view_dim_product_master`
WHERE FlagSalesExc != 'No'
```

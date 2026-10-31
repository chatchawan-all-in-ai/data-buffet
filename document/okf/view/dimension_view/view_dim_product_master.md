---
type: BigQuery View
title: "view_dim_product_master"
description: "ProductSK rows from the barcode-aware product dimension, enriched with marketing segment SKs, rebate exclusion flags and the pump segment."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Product dimension for BI: [dim_product_master](/dimension/dim_product_master.md) (MAC5 stock + MASTERSKU product attributes) plus `FlagSalesExc`/`FlagAccExc` (from [dim_rebate](/dimension/dim_rebate.md), status 'Product') and `PumpSegment` (derived from the marketing segment and the WaterPac code parsed from the product code). The WaterPac name comes from [dim_waterpac](/dimension/dim_waterpac.md). Used by [dim_pump_information](/dimension/dim_pump_information.md); BI model 'Product Master ALL' also reads dim_product_master directly.

# Grain and key

Starts from each dim_product_master row (`ProductSK`; natural key `CompanySK` + `ProductCode` + `Barcode`, with NULL barcode matched as empty). Retained barcode versions can share the same company and product code. The three dim_waterpac joins are 1:1 on CompanySK + upper-case code so they do not multiply rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductSK` | INT64 | SK of the product in dim_product_master (MERGE). |
| `StkMktSK` | INT64 | SK of the stock-marketing mapping in dim_stk_mkt. |
| `ProductMktSK` | INT64 | SK of the marketing classification in dim_product_mkt. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `ProductCode` | STRING | MAC5 stock code (`stkcode`). |
| `ProductCode1` | STRING | Alternate stock code (`stkcode2`). |
| `ProductMac5Description` | STRING | MAC5 stock description (`stkdesct1`). |
| `ProductGroupMAC5` | STRING | MAC5 stock group code (`stg.stgcode`). |
| `ProductGroupMac5Description` | STRING | MAC5 stock group description (Thai). |
| `ProductGroupMAC5Type` | STRING | MAC5 stock group English description (`stgdesce`, used as the group type). |
| `ProductGroupACC` | STRING | Accounting group code (`gacccode`). |
| `ProductGroupACCName` | STRING | Accounting group name (`gaccname`). |
| `ProductName` | STRING | Product name from MASTERSKU `product_detail`. |
| `ProductDescription` | STRING | Product description from MASTERSKU `product`. |
| `ProductDimension1` | STRING | Product dimension 1 from MASTERSKU. |
| `ProductDimension2` | STRING | Product dimension 2 from MASTERSKU. |
| `ProductDimension3` | STRING | Product dimension 3 from MASTERSKU. |
| `ProductDimension4` | STRING | Product dimension 4 from MASTERSKU. |
| `ProductGarantee` | STRING | Warranty text from MASTERSKU (`pd_garantee`; spelling as source). |
| `ProductGaranteeDetail` | STRING | Warranty detail text from MASTERSKU. |
| `ThaiIndustrialStandardFlag` | STRING | Flag derived in dim_product_master from the certificate (Thai Industrial Standard / TIS); exact values not documented here. |
| `ThaiIndustrialSatandardDetail` | STRING | Certificate detail (`pd_certificate`; column spelled `Satandard`). |
| `BrandID` | STRING | Brand id from MASTERSKU product. |
| `VendorID` | STRING | Vendor id from MASTERSKU product. |
| `WarehouseID` | STRING | Default warehouse (`stksto` in MAC5). |
| `Barcode` | STRING | Barcode (`STKcode885`). |
| `FlagSalesExc` | STRING | `salesExc` from dim_rebate (status 'Product') matched on ProductCode and CompanySK; 'No' when none. |
| `FlagAccExc` | STRING | `accExc` from dim_rebate (status 'Product'); 'No' when none. |
| `PumpSegment` | STRING | Pump segment label: WaterPac name for SegmentID 00111/00112, the marketing Segment for MarketingGroupID 002, else 'OTHERS'. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_product_master.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_rebate](/dimension/dim_rebate.md), [dimension_table.dim_waterpac](/dimension/dim_waterpac.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_product_master (operations MERGE, tag `dimension_daily`), dim_product_mkt, dim_rebate, dim_waterpac.

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

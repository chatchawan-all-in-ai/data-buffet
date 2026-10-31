---
type: BigQuery Table
title: "dim_product_master"
description: "One row = one MAC5 stock item (product code) per company and barcode, enriched with MAC5 stock-group, MASTERSKU product master data and marketing-group SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_product_master&page=table"
tags: ["dimension", "mac5", "mastersku", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_product_master.sqlx"
    title: "Dataform definition (dimension/dim_product_master.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Main product dimension. It starts from the MAC5 stock master `stk` (all companies) plus eight dummy ag01 'others' codes for products without an MDT code, adds the MAC5 stock group and accounting group (`stg`), and enriches by barcode (`STKcode885`) with the MASTERSKU product/product_detail (name, description, dimensions, guarantee, certificate, brand, vendor). It also resolves the marketing SKs ([dim_stk_mkt](/dimension/dim_stk_mkt.md), [dim_product_mkt](/dimension/dim_product_mkt.md)). It is the source of `ProductSK` for [fact_order](/fact/fact_order.md), [fact_order_store](/fact/fact_order_store.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_backlog_store](/fact/fact_backlog_store.md), [fact_quotation](/fact/fact_quotation.md), [fact_transcation](/fact/fact_transcation.md) and [fact_transaction_delivery](/fact/fact_transaction_delivery.md), and is exposed as [view_dim_product_master](/view/dimension_view/view_dim_product_master.md).

Used by: [dimension_table.dim_product_mdt](/dimension/dim_product_mdt.md), [fact_table.fact_backlog_store](/fact/fact_backlog_store.md), [fact_table.fact_invoice_store](/fact/fact_invoice_store.md), [fact_table.fact_order](/fact/fact_order.md), [fact_table.fact_order_store](/fact/fact_order_store.md), [dimension_view.view_dim_product_master](/view/dimension_view/view_dim_product_master.md), [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), [onetime.Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [onetime.Product_Master_ALL](/view/onetime/Product_Master_ALL.md), [fact_table.fact_quotation](/fact/fact_quotation.md), [fact_table.fact_transaction_delivery](/fact/fact_transaction_delivery.md), [fact_table.fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per (`CompanySK`, `ProductCode`, `Barcode`) (a missing barcode is matched as an empty string). The source is de-duplicated to one row per `CompanySK` + `ProductCode` (latest MASTERSKU `prd_updated_date`). `ProductSK` is a stable surrogate key assigned at insert (`max_sk + ROW_NUMBER()`); the MERGE matches on the natural key, not on the SK.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductSK` | INT64 | Stable surrogate key of the product; assigned once and never regenerated, stored in facts. |
| `StkMktSK` | INT64 | SK from [dim_stk_mkt](/dimension/dim_stk_mkt.md) matched on stock code and company (marketing attributes per stock code). NULL when the product is not in the marketing master. |
| `ProductMktSK` | INT64 | SK from [dim_product_mkt](/dimension/dim_product_mkt.md), matched via the stock's marketing group, sub-marketing and segment ids. NULL when unmatched. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code of the stock row. |
| `ProductCode` | STRING | MAC5 stock code (`stk.stkcode`); matches `milStk` on lines, but can occur in multiple barcode versions within a company. The dummy codes (OTHERS-style and WAITING999) exist for ag01 only. |
| `ProductCode1` | STRING | Secondary stock code from MAC5 (`stk.stkcode2`). |
| `ProductMac5Description` | STRING | Thai stock description from MAC5 (`stk.stkdesct1`); the fixed Thai text 'special code, product without MDT code' for the dummy codes. |
| `ProductGroupMAC5` | STRING | MAC5 stock group code (`stg.stgcode`, joined from `stk.STKgroup`). |
| `ProductGroupMac5Description` | STRING | Thai stock-group name (`stg.stgdesct`). |
| `ProductGroupMAC5Type` | STRING | Stock-group English description/type (`stg.stgdesce`). |
| `ProductGroupACC` | STRING | Accounting group code (`stg.gacccode`). |
| `ProductGroupACCName` | STRING | Accounting group name (`stg.gaccname`). |
| `ProductName` | STRING | Product name from MASTERSKU `product_detail.pd_product_name`, joined by barcode; NULL if the barcode has no MASTERSKU row. |
| `ProductDescription` | STRING | Product description from MASTERSKU `product.prd_description`. |
| `ProductDimension1` | STRING | Product dimension attribute 1 from MASTERSKU (`prd_dimension1`); unit/meaning not documented in the repo. |
| `ProductDimension2` | STRING | Product dimension attribute 2 from MASTERSKU (`prd_dimension2`). |
| `ProductDimension3` | STRING | Product dimension attribute 3 from MASTERSKU (`prd_dimension3`). |
| `ProductDimension4` | STRING | Product dimension attribute 4 from MASTERSKU (`prd_dimension4`). |
| `ProductGarantee` | STRING | Guarantee/warranty text from MASTERSKU (`pd_garantee`; spelled 'garantee' in the source). |
| `ProductGaranteeDetail` | STRING | Guarantee detail from MASTERSKU (`pd_garantee_detail`). |
| `ThaiIndustrialStandardFlag` | STRING | 'Yes' when MASTERSKU `pd_certificate` is non-empty and not a placeholder ('โปรดระบุ', '-', 'None', 'No'), else 'No' (TIS certification flag). |
| `ThaiIndustrialSatandardDetail` | STRING | Certificate text from MASTERSKU (`pd_certificate`); the column name has the typo 'Satandard'. |
| `BrandID` | STRING | Brand id from MASTERSKU `product.prd_brand_id`. |
| `VendorID` | STRING | Vendor id from MASTERSKU `product.prd_vendor_id`. |
| `WarehouseID` | STRING | Default warehouse/store code from MAC5 `stk.stksto`. |
| `Barcode` | STRING | Barcode `stk.STKcode885`; join key to MASTERSKU and part of the MERGE key. Not updated after insert. |

# How it is built

- Definition: `definitions/dimension/dim_product_master.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [validated_mac5.stk](/validated/validated_mac5/stk.md), [validated_mac5.stg](/validated/validated_mac5/stg.md), [validated_mastersku.product](/validated/validated_mastersku/product.md), [validated_mastersku.product_detail](/validated/validated_mastersku/product_detail.md), [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK on the natural key (`ProductCode` + `Barcode` + `CompanySK`) in a `type: "operations"` file, tag `dimension_daily`; updates all attributes, inserts new products with `max_sk + ROW_NUMBER()`, no delete. Reads all of `stk` each run. Runs after `dim_company`, `dim_stk_mkt` and `dim_product_mkt`; target table pre-exists in BigQuery.
- Approximate size (BigQuery metadata, 2026-10-31): 119,486 rows, 28.6 MB.

# Examples

Products and marketing coverage per company.

```sql
SELECT companyID, COUNT(*) AS products, COUNTIF(StkMktSK IS NOT NULL) AS with_marketing
FROM `databuffet-nonprd.dimension_table.dim_product_master`
GROUP BY companyID
ORDER BY companyID;
```

ProductSK for a company, stock code and known barcode.

```sql
SELECT ProductSK, ProductCode, Barcode, ProductMac5Description, ProductGroupMAC5, BrandID
FROM `databuffet-nonprd.dimension_table.dim_product_master`
WHERE CompanySK = 1 AND ProductCode = 'ABC123'
  AND IFNULL(Barcode, '') = '8851234567890';
```

---
type: BigQuery Table
title: "dim_product_mdt"
description: "One row = one MDT (modern trade saleout) product code with its link to the MAC5 product SK and marketing-group SK, plus placeholder rows for unmapped codes and a -1 unknown row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_product_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_product_mdt
tags: ["dimension", "mds", "saleout", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_product_mdt.sqlx"
    title: "Dataform definition (dimension/dim_product_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Product dimension of the MDT saleout/stock business. The MDS master maps an MDT product code (`product_mdt_code`) to a MAC5 product code; this table resolves that to `ProductSK` ([dim_product_master](/dimension/dim_product_master.md)) and `ProductMktSK` ([dim_product_mkt](/dimension/dim_product_mkt.md)). Product codes seen in the saleout/stock feeds but missing from MDS are added as 'WAITING999' rows. Source: mds `mds_data_mdt_product_master`, plus [curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md) and [curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md) for the placeholders.

Read by: [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [fact_stock_mdt](/fact/fact_stock_mdt.md).

# Grain and key

One row = one MDT product code. Natural key: (`ProductCode`). `ProductMdtSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMdtSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `ProductSK` | INT64 | Foreign key to [dim_product_master](/dimension/dim_product_master.md): the MAC5 product matched on (MAC5 code, company); the company's 'WAITING999' product if none; `-1` if even that is missing. |
| `ProductMktSK` | INT64 | Foreign key to [dim_product_mkt](/dimension/dim_product_mkt.md): from the matched MAC5 product's marketing group, else from the stk-to-marketing mapping ([dim_stk_mkt](/dimension/dim_stk_mkt.md)), else the company's WAITING999 marketing row, else `-1`. |
| `ProductCode` | STRING | MDT product code: mds `product_mdt_code` cast to INT64 and back to STRING (leading zeros stripped); for placeholder rows the feed `product_code` with leading zeros trimmed. 'NotProduct' on the -1 row. |
| `ProductName` | STRING | MDT product name (mds `product_mdt_name`, trimmed); for placeholders the feed name, falling back to the code; Thai 'unspecified product' text on the -1 row. |
| `ProductMac5Code` | STRING | MAC5 product code the MDT code maps to (mds `product_mac5_code`). Set to the literal 'WAITING999' when neither a MAC5 product nor a marketing mapping was found, and for all feed-only placeholder rows; Thai 'no data yet' text on the -1 row. |
| `StoreCode` | STRING | Store/region code of the MDT product (mds `region_id`, or the minimum `store_code` seen in the feeds for placeholders); 'NotStore' on the -1 row. |
| `CompanyID` | STRING | Company code (mds `commpy`, trimmed); placeholders are hard-coded to 'ag01'; 'NotCompany' on the -1 row. Capitalised, as in the source. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_mdt_product_master`; trace column back to MDS. NULL on placeholder and -1 rows (they have no mds source). |
# How it is built

- Definition: `definitions/dimension/dim_product_mdt.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`, `saleout_daily`).
- Reads: [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), `mds_dataset.mds_data_mdt_product_master` (master data loaded outside this repo), [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [curated_saleout_mdt.curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md), [curated_saleout_mdt.curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md).
- CTEs `product_master` (mds), `new_product` (feed-only codes) and `unknown_product` are UNION ALL'd.
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_product_master, dim_stk_mkt and dim_product_mkt.
# Examples

MDT products not yet mapped to a MAC5 product.

```sql
SELECT ProductCode, ProductName, StoreCode, MdsID
FROM `databuffet-nonprd.dimension_table.dim_product_mdt`
WHERE ProductMac5Code = 'WAITING999'
ORDER BY ProductCode;
```

MDT products with their marketing group.

```sql
SELECT m.ProductCode, m.ProductName, k.MarketingGroup, k.SubMarketing
FROM `databuffet-nonprd.dimension_table.dim_product_mdt` m
LEFT JOIN `databuffet-nonprd.dimension_table.dim_product_mkt` k USING (ProductMktSK)
WHERE m.ProductMdtSK <> -1;
```

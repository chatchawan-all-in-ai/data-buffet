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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Product dimension of the MDT saleout/stock business. The MDS master maps an MDT product code (`product_mdt_code`) to a MAC5 product code; this table resolves that to `ProductSK` ([dim_product_master](/dimension/dim_product_master.md)) and `ProductMktSK` ([dim_product_mkt](/dimension/dim_product_mkt.md)) so MDT sales can be reported by marketing group. Product codes seen in the saleout/stock feeds but missing from MDS are added automatically as 'WAITING999' rows so facts never lose rows. Used by [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md) and [fact_stock_mdt](/fact/fact_stock_mdt.md). Source: mds `mds_data_mdt_product_master`, plus [curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md) and [curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md) for the placeholders.

# Grain and key

One row per MDT product code (`ProductCode`, the integer MDT code as text). Mds rows are deduped on `product_mdt_code` (preferring rows that have a MAC5 code, then lowest region id, then id). Key: `ProductMdtSK` (surrogate, unstable across days), plus the reserved `-1` row (ProductCode 'NotProduct').

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMdtSK` | INT64 | For mds rows `ROW_NUMBER() OVER(ORDER BY CAST(product_mdt_code AS INT64))`; for feed-only placeholder rows `MAX(mds SK) + ROW_NUMBER()` ordered by product code; `-1` for the unknown row. Regenerates every run. |
| `ProductSK` | INT64 | Foreign key to [dim_product_master](/dimension/dim_product_master.md): the MAC5 product matched on (MAC5 code, company); the company's 'WAITING999' product if none; `-1` if even that is missing. |
| `ProductMktSK` | INT64 | Foreign key to [dim_product_mkt](/dimension/dim_product_mkt.md): from the matched MAC5 product's marketing group, else from the stk-to-marketing mapping ([dim_stk_mkt](/dimension/dim_stk_mkt.md)), else the company's WAITING999 marketing row, else `-1`. |
| `ProductCode` | STRING | MDT product code: mds `product_mdt_code` cast to INT64 and back to STRING (leading zeros stripped); for placeholder rows the feed `product_code` with leading zeros trimmed. 'NotProduct' on the -1 row. |
| `ProductName` | STRING | MDT product name (mds `product_mdt_name`, trimmed); for placeholders the feed name, falling back to the code; Thai 'unspecified product' text on the -1 row. |
| `ProductMac5Code` | STRING | MAC5 product code the MDT code maps to (mds `product_mac5_code`). Set to the literal 'WAITING999' when neither a MAC5 product nor a marketing mapping was found, and for all feed-only placeholder rows; Thai 'no data yet' text on the -1 row. |
| `StoreCode` | STRING | Store/region code of the MDT product (mds `region_id`, or the minimum `store_code` seen in the feeds for placeholders); 'NotStore' on the -1 row. |
| `CompanyID` | STRING | Company code (mds `commpy`, trimmed); placeholders are hard-coded to 'ag01'; 'NotCompany' on the -1 row. Capitalised, as in the source. |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. NULL on placeholder and -1 rows (they have no mds source). |

# How it is built

- Definition: `definitions/dimension/dim_product_mdt.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `ProductMdtSK`.
- Storage options: `{"clusterBy": ["ProductMdtSK"]}`.
- Reads: [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), `mds_dataset.mds_data_mdt_product_master` (master data loaded outside this repo), [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [curated_saleout_mdt.curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md), [curated_saleout_mdt.curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md).
- Full daily rebuild (`type: "table"`, tags `dimension_daily` and the saleout daily tag): CTEs `product_master` (mds), `new_product` (feed-only codes), `unknown_product` UNION ALL'd. Depends on `dim_product_master`, `dim_stk_mkt`, `dim_product_mkt` and reads the three `curated_saleout_mdt` tables via `ref()`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,526 rows, 446.7 KB.

# Examples

MDT products not yet mapped to a MAC5 product (need MDS maintenance).

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

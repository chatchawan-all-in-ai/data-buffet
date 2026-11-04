---
type: BigQuery Table
title: "dim_product_mkt"
description: "One row = one marketing classification (type, marketing group, sub-marketing, segment) per company, from the MDS marketing-name master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_product_mkt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_product_mkt
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_product_mkt.sqlx"
    title: "Dataform definition (dimension/dim_product_mkt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Product marketing hierarchy: TypeMarketing, then MarketingGroup, SubMarketing and Segment, each with an id and a name. Facts and dimensions point to it with `ProductMktSK` to report sales, orders, backlog, targets and saleout by marketing group. Consumers include [dim_product_mdt](/dimension/dim_product_mdt.md), [dim_pump_information](/dimension/dim_pump_information.md), [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [dim_target_saleout_mdt](/dimension/dim_target_saleout_mdt.md), [fact_backlog_store](/fact/fact_backlog_store.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_order_store](/fact/fact_order_store.md) and [fact_saleout_mdt](/fact/fact_saleout_mdt.md). Source: mds `mds_data_product_marketing_name_master`.

# Grain and key

One row per (company, TypeMarketingID, MarketingGroupID, SubMarketingID, SegmentID) among active mds rows. Key: `ProductMktSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMktSK` | INT64 | `ProductMktSK` is `ROW_NUMBER() OVER(ORDER BY CompanyID, TypeMarketingID, MarketingGroupID, SubMarketingID, SegmentID)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `CompanyID`; natural join key to dim_company.companyID. |
| `TypeMarketingID` | STRING | Pass-through of mds `TypeMarketingID`, cleaned with `cleanString` (empty string becomes NULL). Top level id of the marketing hierarchy; joins to [dim_product_mkt_director](/dimension/dim_product_mkt_director.md).TypeMarketingID. |
| `TypeMarketing` | STRING | Pass-through of mds `TypeMarketing`, cleaned with `cleanString` (empty string becomes NULL). Name of the marketing type. |
| `MarketingGroupID` | STRING | Pass-through of mds `MarketingGroupID`, cleaned with `cleanString` (empty string becomes NULL). Marketing group id (level 2); also used to join PCs in [dim_pc](/dimension/dim_pc.md). |
| `MarketingGroup` | STRING | Pass-through of mds `MarketingGroup`, cleaned with `cleanString` (empty string becomes NULL). Marketing group name. |
| `SubMarketingID` | STRING | Pass-through of mds `SubMarketingID`, cleaned with `cleanString` (empty string becomes NULL). Sub-marketing id (level 3). |
| `SubMarketing` | STRING | Pass-through of mds `SubMarketing`, cleaned with `cleanString` (empty string becomes NULL). Sub-marketing name. |
| `SegmentID` | STRING | Pass-through of mds `SegmentID`, cleaned with `cleanString` (empty string becomes NULL). Segment id (level 4). |
| `Segment` | STRING | Pass-through of mds `Segment`, cleaned with `cleanString` (empty string becomes NULL). Segment name. |
| `SubMarketingWH` | STRING | Pass-through of mds `SubMarketingWH`, cleaned with `cleanString` (empty string becomes NULL). Warehouse reporting group of the sub-marketing group, a coarser grouping such as `DIY`, `ROTO`, `BLOW`, `LITE TITE` or `OTHERS`. |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_product_mkt.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `ProductMktSK`.
- Storage options: `{"clusterBy": ["ProductMktSK"]}`.
- Reads: `mds_dataset.mds_data_product_marketing_name_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows (`is_active = TRUE`); runs after dim_company (declared dependency).

# Examples

The marketing hierarchy for one company.

```sql
SELECT TypeMarketing, MarketingGroup, SubMarketing, Segment, ProductMktSK
FROM `databuffet-nonprd.dimension_table.dim_product_mkt`
WHERE CompanyID = 'ag01'
ORDER BY TypeMarketingID, MarketingGroupID, SubMarketingID, SegmentID;
```

Duplicate five-part keys.

```sql
SELECT CompanyID, TypeMarketingID, MarketingGroupID, SubMarketingID, SegmentID, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_product_mkt`
GROUP BY 1, 2, 3, 4, 5
HAVING n > 1;
```

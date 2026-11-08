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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Product marketing hierarchy: TypeMarketing, then MarketingGroup, SubMarketing and Segment, each with an id and a name. Source: mds `mds_data_product_marketing_name_master`.

Read by: [dim_product_master](/dimension/dim_product_master.md), [dim_product_mdt](/dimension/dim_product_mdt.md), [dim_pump_information](/dimension/dim_pump_information.md), [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [dim_target_saleout_mdt](/dimension/dim_target_saleout_mdt.md), [fact_backlog_store](/fact/fact_backlog_store.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_order_store](/fact/fact_order_store.md), [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [fact_transcation](/fact/fact_transcation.md), [rls_customer360](/process/rls_customer360.md), [view_dim_product_master](/view/dimension_view/view_dim_product_master.md), [view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_fact_saleout_pc_mdt](/view/fact_view/view_fact_saleout_pc_mdt.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md).

# Grain and key

One row = one marketing classification per company. Natural key: (`CompanyID`, `TypeMarketingID`, `MarketingGroupID`, `SubMarketingID`, `SegmentID`). `ProductMktSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMktSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `CompanyID`; natural join key to dim_company.companyID. |
| `TypeMarketingID` | STRING | Pass-through of mds `TypeMarketingID`, cleaned with `cleanString` (empty string becomes NULL). Top level id of the marketing hierarchy; joins to [dim_product_mkt_director](/dimension/dim_product_mkt_director.md).TypeMarketingID. |
| `TypeMarketing` | STRING | Pass-through of mds `TypeMarketing`, cleaned with `cleanString` (empty string becomes NULL). Name of the marketing type. |
| `MarketingGroupID` | STRING | Pass-through of mds `MarketingGroupID`, cleaned with `cleanString` (empty string becomes NULL). Marketing group id (level 2); [view_fact_saleout_pc_mdt](/view/fact_view/view_fact_saleout_pc_mdt.md) matches it to `dim_pc.MarketingGroupID`. |
| `MarketingGroup` | STRING | Pass-through of mds `MarketingGroup`, cleaned with `cleanString` (empty string becomes NULL). Marketing group name. |
| `SubMarketingID` | STRING | Pass-through of mds `SubMarketingID`, cleaned with `cleanString` (empty string becomes NULL). Sub-marketing id (level 3). |
| `SubMarketing` | STRING | Pass-through of mds `SubMarketing`, cleaned with `cleanString` (empty string becomes NULL). Sub-marketing name. |
| `SegmentID` | STRING | Pass-through of mds `SegmentID`, cleaned with `cleanString` (empty string becomes NULL). Segment id (level 4). |
| `Segment` | STRING | Pass-through of mds `Segment`, cleaned with `cleanString` (empty string becomes NULL). Segment name. |
| `SubMarketingWH` | STRING | Pass-through of mds `SubMarketingWH`, cleaned with `cleanString` (empty string becomes NULL). Warehouse reporting group of the sub-marketing group, a coarser grouping such as `DIY`, `ROTO`, `BLOW`, `LITE TITE` or `OTHERS`. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_product_marketing_name_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_product_mkt.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_product_marketing_name_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
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

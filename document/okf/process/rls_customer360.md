---
type: BigQuery Table
title: "rls_customer360"
description: "One row = one customer (milCus) with the pipe-delimited lists of every salesperson, section, region, director and product-marketing combination associated with that customer in the transaction fact."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=rls_customer360&page=table"
tags: ["process", "RLS"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/process/rls_customer360.sqlx"
    title: "Dataform definition (process/rls_customer360.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Customer-to-organisation access map used for row-level security (RLS) on Customer360: it tells downstream views which sales entities touch each customer, so they can decide who may see that customer. It is built from fact_transcation joined to dim_section, dim_region, dim_director and dim_product_mkt, and is read by [view_rls_sale_data](/view/process_dataset/view_rls_sale_data.md) (matches a sales user's section via `SectionID`) and [view_rls_special_data](/view/process_dataset/view_rls_special_data.md). It holds no AI and no CDC gate.

# Grain and key

One row per `milCus` (customer code in the fact; it does not carry company_id, so the same code in different companies is merged into one row). All other columns are `STRING_AGG(DISTINCT ..., '|')` over every fact row of that customer.

# Schema

| Column | Type | Description |
|---|---|---|
| `milCus` | STRING | Customer code (fact_transcation.milCus). The grain; no company column. |
| `milPer` | STRING | Pipe-separated distinct salesperson codes (fact milPer) that sold to the customer. |
| `SectionID` | STRING | Pipe-separated distinct section ids (dim_section.SectionID, via the fact's SectionSK); NULL when the fact rows have no section. |
| `RegionID` | STRING | Pipe-separated distinct region ids (dim_region.RegionID, via RegionSK). |
| `DirectorID` | STRING | Pipe-separated distinct director ids (dim_director.DirectorID, via DirectorSK). |
| `ProductMkt` | STRING | Pipe-separated distinct combinations `MarketingGroupID:SubMarketingID:SegmentID` from dim_product_mkt (via ProductMktSK); a combo with a NULL part is dropped by CONCAT (becomes NULL and is ignored by STRING_AGG). |

# How it is built

- Definition: `definitions/process/rls_customer360.sqlx` (`type: "table"`, tags `process`).
- Reads: [fact_table.fact_transcation](/fact/fact_transcation.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md).
- Full daily rebuild (`type: "table"`, tag `process`; dependencies fact_transcation, dim_region, dim_section, dim_director, dim_product_mkt, so it runs after the fact and dimensions). It inherits the coverage of fact_transcation (about 4 years rolling).
- Approximate size (BigQuery metadata, 2026-10-31): 29,715 rows, 2.7 MB.

# Examples

Which sections can see a customer.

```sql
SELECT milCus, SectionID, RegionID, DirectorID
FROM `databuffet-nonprd.process_dataset.rls_customer360`
WHERE milCus = 'REPLACE_WITH_CUSTOMER_CODE'
```

Customers visible to one section.

```sql
SELECT milCus
FROM `databuffet-nonprd.process_dataset.rls_customer360`,
     UNNEST(SPLIT(SectionID, '|')) AS sec
WHERE sec = 'REPLACE_WITH_SECTION_ID'
```

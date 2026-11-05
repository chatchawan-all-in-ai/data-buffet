---
type: BigQuery View
title: "view_dim_product_mkt"
description: "One row = one product marketing classification with each matching director record, or NULL when unmatched; ProductMktSK repeats when several director records match."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_product_mkt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_product_mkt
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_product_mkt.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_product_mkt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Marketing hierarchy view: [dim_product_mkt](/dimension/dim_product_mkt.md) (type > marketing group > sub-marketing > segment, from MDS) with `ProductMktDirectorSK` from [dim_product_mkt_director](/dimension/dim_product_mkt_director.md), matched on TypeMarketingID and CompanyID. Read by [Product_Master_ALL](/view/onetime/Product_Master_ALL.md). Exported by [export_view_dim_product_mkt](/view/pub_sub/export_view_dim_product_mkt.md).

# Grain and key

One row = one dim_product_mkt row x one dim_product_mkt_director row with the same TypeMarketingID and CompanyID (LEFT JOIN, no StartDate/EndDate filter, no director deduplication); `ProductMktDirectorSK` is NULL when none matches. `ProductMktSK` repeats when several director records match, so it is not a unique key of the view. Natural hierarchy: TypeMarketingID > MarketingGroupID > SubMarketingID > SegmentID per company.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMktSK` | INT64 | SK of the marketing classification in dim_product_mkt (regenerated daily). |
| `ProductMktDirectorSK` | INT64 | SK of one director record matched on TypeMarketingID + CompanyID without a date filter; NULL if none. Each matching director record yields its own view row. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `CompanyID` | STRING | MAC5 company code. |
| `TypeMarketingID` | STRING | Marketing type code (top level). |
| `TypeMarketing` | STRING | Marketing type name. |
| `MarketingGroupID` | STRING | Marketing group code (level 2). |
| `MarketingGroup` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing code (level 3). |
| `SubMarketing` | STRING | Sub-marketing name. |
| `SegmentID` | STRING | Segment code (level 4). |
| `Segment` | STRING | Segment name. |
| `SubMarketingWH` | STRING | Warehouse reporting group of the sub-marketing group, a coarser grouping such as `DIY`, `ROTO`, `BLOW`, `LITE TITE` or `OTHERS`. |
| `MdsID` | STRING | Id of the source row in the MDS master (trace column). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_product_mkt.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_product_mkt_director](/dimension/dim_product_mkt_director.md).

# Examples

Marketing hierarchy for one company:

```sql
SELECT DISTINCT TypeMarketing, MarketingGroup, SubMarketing, Segment
FROM `databuffet-nonprd.dimension_view.view_dim_product_mkt`
WHERE CompanyID = 'ag01'
ORDER BY TypeMarketing, MarketingGroup, SubMarketing, Segment
```

Classification rows with no matching director record:

```sql
SELECT COUNT(*) AS rows
FROM `databuffet-nonprd.dimension_view.view_dim_product_mkt`
WHERE ProductMktDirectorSK IS NULL
```

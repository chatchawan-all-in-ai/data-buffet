---
type: BigQuery View
title: "view_dim_product_mkt"
description: "One row = one product marketing classification with each matching director record, or NULL when unmatched; retained director intervals can repeat ProductMktSK."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_product_mkt&page=table"
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_product_mkt.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_product_mkt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Marketing hierarchy view: [dim_product_mkt](/dimension/dim_product_mkt.md) (type > marketing group > sub-marketing > segment, from MDS) with `ProductMktDirectorSK` from [dim_product_mkt_director](/dimension/dim_product_mkt_director.md), matched on TypeMarketingID and CompanyID. Used by [Product_Master_ALL](/view/onetime/Product_Master_ALL.md). The director join has no date filter, so retained previous and current intervals can both match.

# Grain and key

Each dim_product_mkt row joins every dim_product_mkt_director row with the same TypeMarketingID and CompanyID, without StartDate/EndDate filtering or director deduplication. One row remains with NULL director SK when none matches. ProductMktSK is therefore repeated when a type has several retained director records; it is not a unique view key. Natural hierarchy: TypeMarketingID > MarketingGroupID > SubMarketingID > SegmentID per company.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMktSK` | INT64 | SK of the marketing classification in dim_product_mkt (regenerated daily). |
| `ProductMktDirectorSK` | INT64 | SK of one director record matched on TypeMarketingID + CompanyID; NULL if none. Multiple intervals yield multiple view rows, and the match does not imply validity on the query or fact date. |
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
| `MdsId` | STRING | Id of the source row in the MDS master (trace column). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_product_mkt.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_product_mkt_director](/dimension/dim_product_mkt_director.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_product_mkt and dim_product_mkt_director (both full rebuilds from mds, tag `dimension_daily`).

# Examples

Marketing hierarchy for one company from the classification dimension:

```sql
SELECT TypeMarketing, MarketingGroup, SubMarketing, Segment
FROM `databuffet-nonprd.dimension_table.dim_product_mkt`
WHERE CompanyID = 'ag01'
ORDER BY TypeMarketingID, MarketingGroupID, SubMarketingID, SegmentID
```

Classification rows with no matching director record at any retained interval (not a test of director coverage on a particular date):

```sql
SELECT COUNT(*) AS segments
FROM `databuffet-nonprd.dimension_view.view_dim_product_mkt`
WHERE ProductMktDirectorSK IS NULL
```

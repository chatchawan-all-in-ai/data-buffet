---
type: BigQuery Table
title: "dim_pump_information"
description: "One row = one distinct combination of company, product code (milstk), RegionID and FlagNewProductMKT seen in fact_transcation, with the pump segment resolved for it."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_pump_information&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_pump_information
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_pump_information.sqlx"
    title: "Dataform definition (dimension/dim_pump_information.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Lookup that gives every transaction line its pump segment (PumpSegment) per product and region. For region PS1 with the new-product-market flag the segment comes from `dim_product_mkt.Segment`; for everything else it is `PumpSegment` of `view_dim_product_master`. `view_fact_transcation` joins it to expose `PumpSK`. It is the only dimension that is derived from a fact table.

Read by: [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

Built from `SELECT DISTINCT` over fact_transcation lines with `milStk` not NULL, joined to the product master view, dim_region and dim_product_mkt; the distinct key is `(CompanySK, CompanyID, milstk, RegionID, FlagNewProductMKT, PumpSegment)`. Consumers join on `(LOWER(milstk), FlagNewProductMKT, RegionID, CompanySK)`, so a key with two different PumpSegment values would fan out. SK ordered by lower(milstk), RegionID, FlagNewProductMKT. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `PumpSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by lower(milstk), RegionID, FlagNewProductMKT. Regenerated every run. |
| `CompanySK` | INT64 | Company SK copied from `fact_transcation.CompanySK`. |
| `CompanyID` | STRING | Company code copied from `fact_transcation.CompanyID`. |
| `milstk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `RegionID` | STRING | Region code of the line, from dim_region via `fact_transcation.RegionSK`; NULL when the line has no region. |
| `FlagNewProductMKT` | BOOL | BOOL flag copied from `fact_transcation.FlagNewProductMKT`; true when the line uses the new product-market mapping (`NewProductMktSK`). |
| `PumpSegment` | STRING | Pump segment: `dim_product_mkt.Segment` when RegionID is 'PS1' and FlagNewProductMKT is true, otherwise `view_dim_product_master.PumpSegment`. |

# How it is built

- Definition: `definitions/dimension/dim_pump_information.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `PumpSK`.
- Storage options: `{"clusterBy": ["PumpSK"]}`.
- Reads: [fact_table.fact_transcation](/fact/fact_transcation.md), [dimension_view.view_dim_product_master](/view/dimension_view/view_dim_product_master.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`, but it reads `fact_transcation` (tag `fact_daily`); config dependencies are fact_transcation, dim_product_mkt, dim_product_master and dim_region.
- Approximate size (BigQuery metadata, 2026-10-31): 35,575 rows, 1.7 MB.

# Examples

Pump segment per product and region.

```sql
SELECT CompanyID, milstk, RegionID, FlagNewProductMKT, PumpSegment
FROM `databuffet-nonprd.dimension_table.dim_pump_information`
WHERE CompanyID = 'ag01'
ORDER BY milstk, RegionID
LIMIT 100;
```

Row count per pump segment.

```sql
SELECT PumpSegment, COUNT(*) AS combos
FROM `databuffet-nonprd.dimension_table.dim_pump_information`
GROUP BY PumpSegment
ORDER BY combos DESC;
```

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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Lookup that gives every transaction line its pump segment (PumpSegment) per product and region. For region PS1 with the new-product-market flag the segment comes from `dim_product_mkt.Segment`; for everything else it is `PumpSegment` of `view_dim_product_master`.

Read by: [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [export_dim_pump_information](/view/pub_sub/export_dim_pump_information.md).

# Grain and key

One row = one distinct combination `(CompanySK, CompanyID, milstk, RegionID, FlagNewProductMKT, PumpSegment)` taken with `SELECT DISTINCT` over fact_transcation lines with `milStk` not NULL, joined to the product master view, dim_region and dim_product_mkt. Natural key: (`CompanyID`, `milstk`, `RegionID`, `FlagNewProductMKT`, `PumpSegment`). `PumpSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `PumpSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Copied from `fact_transcation.CompanySK`; NULL when that source value is NULL. |
| `CompanyID` | STRING | Company code copied from `fact_transcation.CompanyID`. |
| `milstk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `RegionID` | STRING | Region code of the line, from dim_region via `fact_transcation.RegionSK`; NULL when the line has no region. |
| `FlagNewProductMKT` | BOOL | BOOL flag copied from `fact_transcation.FlagNewProductMKT`; true when the line uses the new product-market mapping (`NewProductMktSK`). |
| `PumpSegment` | STRING | Pump segment: `dim_product_mkt.Segment` when RegionID is 'PS1' and FlagNewProductMKT is true, otherwise `view_dim_product_master.PumpSegment`. |
# How it is built

- Definition: `definitions/dimension/dim_pump_information.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: [fact_table.fact_transcation](/fact/fact_transcation.md), [dimension_view.view_dim_product_master](/view/dimension_view/view_dim_product_master.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after fact_transcation, dim_product_mkt, dim_product_master and dim_region.
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

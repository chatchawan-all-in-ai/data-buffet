---
type: BigQuery Table
title: "dim_cost_group"
description: "One row = one standard-cost percentage for a product group (GAccID) in a cost channel for a validity period, per company."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_cost_group&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_cost_group
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_cost_group.sqlx"
    title: "Dataform definition (dimension/dim_cost_group.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Standard-cost rate table by product group. [fact_transcation](/fact/fact_transcation.md) stores a `CostGroupSK` per sales line and [view_fact_transcation](/view/fact_view/view_fact_transcation.md) joins it back on `CostGroupSK` + `CompanySK` to compute `ProductPercent` (the group-level cost ratio, used when no product-level row from [dim_cost_stk](/dimension/dim_cost_stk.md) applies). Source: mds `mds_data_standard_cost_by_product_group_master`.

Read by: [fact_transcation](/fact/fact_transcation.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one standard-cost rate of a product group and cost channel for a validity period. Natural key: (`companyID`, `GAccID`, `ChannelCostID`, `StartDate`, `EndDate`). `CostGroupSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `CostGroupSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `GAccID` | STRING | Pass-through of mds `GAccID`, cleaned with `cleanString` (empty string becomes NULL). Product group account code (G-account); the group-level key. |
| `GAccName` | STRING | Pass-through of mds `GAccName`, cleaned with `cleanString` (empty string becomes NULL). Product group account name. |
| `ChannelCostID` | STRING | Pass-through of mds `ChannelCostID`, cleaned with `cleanString` (empty string becomes NULL). Cost channel code, see [dim_channel_cost](/dimension/dim_channel_cost.md). |
| `ChannelCostName` | STRING | Pass-through of mds `ChannelCostName`, cleaned with `cleanString` (empty string becomes NULL). Cost channel name. |
| `Percent` | FLOAT64 | Standard cost as a percentage of sales for this product group and cost channel (`castFloat64` of mds `Percent`); view_fact_transcation divides it by 100 (`ROUND(Percent/100, 4)`) to get `ProductPercent`. |
| `StartDate` | DATE | First day the percentage is valid (mds `StartDate`, DATE). |
| `EndDate` | DATE | Last day the percentage is valid (mds `EndDate`, DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_standard_cost_by_product_group_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_cost_group.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`).
- Reads: `mds_dataset.mds_data_standard_cost_by_product_group_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Standard-cost percent per group and cost channel valid today.

```sql
SELECT companyID, GAccID, ChannelCostID, Percent
FROM `databuffet-nonprd.dimension_table.dim_cost_group`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

Duplicate active keys.

```sql
SELECT companyID, GAccID, ChannelCostID, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_cost_group`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
GROUP BY 1, 2, 3
HAVING n > 1;
```

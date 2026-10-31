---
type: BigQuery Table
title: "dim_cost_stk"
description: "One row = one product-level (MilStk) standard-cost percentage in a cost channel for a validity period, per company."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_cost_stk&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_cost_stk
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_cost_stk.sqlx"
    title: "Dataform definition (dimension/dim_cost_stk.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Standard-cost rates at product level, the more specific counterpart of [dim_cost_group](/dimension/dim_cost_group.md). [fact_transcation](/fact/fact_transcation.md) stores `CostStkSK`; [view_fact_transcation](/view/fact_view/view_fact_transcation.md) joins `CostStkSK` + `CompanySK` and uses `Percent/100` as `ProductPercent` when present. Source: mds `mds_data_standard_cost_by_product_id_master`.

# Grain and key

One row per (company, MilStk, GaccID, ChannelCostID, StartDate, EndDate) among active mds rows. Key: `CostStkSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `CostStkSK` | INT64 | `CostStkSK` is `ROW_NUMBER() OVER(ORDER BY companyID, MilStk, GaccID, ChannelCostID, StartDate, EndDate)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `MilStk` | STRING | Pass-through of mds `MilStk`, cleaned with `cleanString` (empty string becomes NULL). Product code as on the sales line (`milstk`); product-level key. |
| `GaccID` | STRING | Pass-through of mds `GaccID`, cleaned with `cleanString` (empty string becomes NULL). Product group account code (lower-case `acc` here versus `GAccID` in dim_cost_group). |
| `GAccName` | STRING | Pass-through of mds `GAccName`, cleaned with `cleanString` (empty string becomes NULL). Product group account name. |
| `ChannelCostID` | STRING | Pass-through of mds `ChannelCostID`, cleaned with `cleanString` (empty string becomes NULL). Cost channel code, see [dim_channel_cost](/dimension/dim_channel_cost.md). |
| `ChannelCostName` | STRING | Pass-through of mds `ChannelCostName`, cleaned with `cleanString` (empty string becomes NULL). Cost channel name. |
| `Percent` | FLOAT64 | Standard cost as a percentage of sales for this specific product and cost channel (`castFloat64` of mds `Percent`); view_fact_transcation divides it by 100 to get `ProductPercent`. |
| `StartDate` | DATE | First day the percentage is valid (mds `StartDate`, DATE). |
| `EndDate` | DATE | Last day the percentage is valid (mds `EndDate`, DATE). |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_cost_stk.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `CostStkSK`.
- Storage options: `{"clusterBy": ["CostStkSK"]}`.
- Reads: `mds_dataset.mds_data_standard_cost_by_product_id_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows (`is_active = TRUE`); runs after dim_company (declared dependency).
- Approximate size (BigQuery metadata, 2026-10-31): 6,446 rows, 1.2 MB.

# Examples

Product-level standard cost percent valid today.

```sql
SELECT companyID, MilStk, ChannelCostID, Percent
FROM `databuffet-nonprd.dimension_table.dim_cost_stk`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

Number of product cost rows per company and cost channel.

```sql
SELECT companyID, ChannelCostID, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_cost_stk`
GROUP BY 1, 2
ORDER BY 1, 2;
```

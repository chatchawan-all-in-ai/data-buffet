---
type: BigQuery Table
title: "dim_channel_cost"
description: "One row = one cost channel (code and name) per company, from the MDS cost-channel master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_channel_cost&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_channel_cost
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_channel_cost.sqlx"
    title: "Dataform definition (dimension/dim_channel_cost.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Lookup of cost channels used to allocate cost and standard-cost percentages. [fact_transcation](/fact/fact_transcation.md) stores `ChannelCostSK` from it. The cost-percentage dims [dim_cost_group](/dimension/dim_cost_group.md) and [dim_cost_stk](/dimension/dim_cost_stk.md) carry the same `ChannelCostID`. Source: mds `mds_data_channel_cost_master`.

Read by: [view_dim_channel](/view/dimension_view/view_dim_channel.md), [fact_transcation](/fact/fact_transcation.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md).

# Grain and key

One row = one cost channel of a company among active mds rows. Natural key: (`companyID`, `ChannelCostID`). `ChannelCostSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `ChannelCostSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `ChannelCostID` | STRING | Pass-through of mds `ChannelCostID`, cleaned with `cleanString` (empty string becomes NULL). Natural key with companyID. |
| `ChannelCostName` | STRING | Pass-through of mds `ChannelCostName`, cleaned with `cleanString` (empty string becomes NULL). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_channel_cost_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_channel_cost.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`).
- Reads: `mds_dataset.mds_data_channel_cost_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Codes and names for one company.

```sql
SELECT ChannelCostID, ChannelCostName
FROM `databuffet-nonprd.dimension_table.dim_channel_cost`
WHERE companyID = 'ag01'
ORDER BY ChannelCostID;
```

Duplicate natural keys.

```sql
SELECT companyID, ChannelCostID, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_channel_cost`
GROUP BY 1, 2
HAVING n > 1;
```

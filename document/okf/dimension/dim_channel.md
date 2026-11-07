---
type: BigQuery Table
title: "dim_channel"
description: "One row = one department code (DepCode) per company with its sales, cost and finance channel classification, from the MDS channel master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_channel&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_channel
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_channel.sqlx"
    title: "Dataform definition (dimension/dim_channel.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Wide channel master that maps a ledger department code to three channel hierarchies at once: sales channel (`ChannelID`), cost channel (`ChannelCostID`) and finance channel (`ChannelIDFinance`), plus the D-site/department/division/sub-division levels. [view_dim_channel](/view/dimension_view/view_dim_channel.md) combines it with the narrower [dim_channel_sales](/dimension/dim_channel_sales.md), [dim_channel_cost](/dimension/dim_channel_cost.md) and [dim_channel_finance](/dimension/dim_channel_finance.md). Source is mds `mds_data_channel_master`.

Read by: [view_dim_channel](/view/dimension_view/view_dim_channel.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md).

# Grain and key

One row = one department code of a company among active mds rows. Natural key: (`companyID`, `DepCode`). `ChannelSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `ChannelSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `DepCode` | STRING | Department/cost-centre code from the ledger (`DepCode`); the natural key with companyID and the join key from sales documents. |
| `DepGroup` | STRING | Pass-through of mds `DepGroup`, cleaned with `cleanString` (empty string becomes NULL). Department group code, e.g. `M35`, `MK4`, `HY`, `UB`. |
| `DepDesct` | STRING | Pass-through of mds `DepDesct`, cleaned with `cleanString` (empty string becomes NULL). Department description in Thai. |
| `DepDesce` | STRING | Pass-through of mds `DepDesce`, cleaned with `cleanString` (empty string becomes NULL). Department description in English (often NULL). |
| `ChannelGroup` | STRING | Pass-through of mds `ChannelGroup`, cleaned with `cleanString` (empty string becomes NULL). Top level of the sales-channel hierarchy. |
| `ChannelSubGroupName1` | STRING | Pass-through of mds `ChannelSubGroupName1`, cleaned with `cleanString` (empty string becomes NULL). Sales-channel hierarchy level 1 below ChannelGroup. |
| `ChannelSubGroupName2` | STRING | Pass-through of mds `ChannelSubGroupName2`, cleaned with `cleanString` (empty string becomes NULL). Sales-channel hierarchy level 2. |
| `ChannelSubGroupName3` | STRING | Pass-through of mds `ChannelSubGroupName3`, cleaned with `cleanString` (empty string becomes NULL). Sales-channel hierarchy level 3. |
| `ChannelID` | STRING | Pass-through of mds `ChannelID`, cleaned with `cleanString` (empty string becomes NULL). Sales channel code; joins to ChannelID in [dim_channel_sales](/dimension/dim_channel_sales.md). |
| `ChannelName` | STRING | Pass-through of mds `ChannelName`, cleaned with `cleanString` (empty string becomes NULL). Sales channel name. |
| `ChannelCostID` | STRING | Pass-through of mds `ChannelCostID`, cleaned with `cleanString` (empty string becomes NULL). Cost channel code; joins to [dim_channel_cost](/dimension/dim_channel_cost.md).ChannelCostID. |
| `ChannelCostName` | STRING | Pass-through of mds `ChannelCostName`, cleaned with `cleanString` (empty string becomes NULL). Cost channel name. |
| `ChannelGroupFinance` | STRING | Pass-through of mds `ChannelGroupFinance`, cleaned with `cleanString` (empty string becomes NULL). Top level of the finance-channel hierarchy. |
| `ChannelSubGroupFinance1` | STRING | Pass-through of mds `ChannelSubGroupFinance1`, cleaned with `cleanString` (empty string becomes NULL). Finance-channel hierarchy level 1. |
| `ChannelSubGroupFinance2` | STRING | Pass-through of mds `ChannelSubGroupFinance2`, cleaned with `cleanString` (empty string becomes NULL). Finance-channel hierarchy level 2. |
| `ChannelSubGroupFinance3` | STRING | Pass-through of mds `ChannelSubGroupFinance3`, cleaned with `cleanString` (empty string becomes NULL). Finance-channel hierarchy level 3. |
| `ChannelIDFinance` | STRING | Pass-through of mds `ChannelIDFinance`, cleaned with `cleanString` (empty string becomes NULL). Finance channel code; joins to [dim_channel_finance](/dimension/dim_channel_finance.md).ChannelIDFinance. |
| `ChannelNameFinance` | STRING | Pass-through of mds `ChannelNameFinance`, cleaned with `cleanString` (empty string becomes NULL). Finance channel name. |
| `ChannelDSite01` | STRING | Pass-through of mds `ChannelDSite01`, cleaned with `cleanString` (empty string becomes NULL). Level 1 (site) of the D-channel hierarchy site > department > division > sub-division, e.g. `HO1`, `HY1`, `KTB`, `Other`. |
| `ChannelDDepartment02` | STRING | Pass-through of mds `ChannelDDepartment02`, cleaned with `cleanString` (empty string becomes NULL). Dimension-style channel level 2 (Department). |
| `ChannelDDivision03` | STRING | Pass-through of mds `ChannelDDivision03`, cleaned with `cleanString` (empty string becomes NULL). Dimension-style channel level 3 (Division). |
| `ChannelDSubDivision04` | STRING | Pass-through of mds `ChannelDSubDivision04`, cleaned with `cleanString` (empty string becomes NULL). Dimension-style channel level 4 (Sub-division). |
| `DummyChannel` | STRING | Pass-through of mds `DummyChannel`, cleaned with `cleanString` (empty string becomes NULL). Dummy employee id (e.g. `9999991`, `9999994`) that fact_transcation uses in place of the line salesperson when matching sales representatives; `not calculated` when the department has none. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_channel_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_channel.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`).
- Reads: `mds_dataset.mds_data_channel_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Sales, cost and finance channels for a department code.

```sql
SELECT companyID, DepCode, ChannelID, ChannelName, ChannelCostID, ChannelIDFinance
FROM `databuffet-nonprd.dimension_table.dim_channel`
WHERE companyID = 'ag01'
ORDER BY DepCode;
```

Duplicate (companyID, DepCode) keys.

```sql
SELECT companyID, DepCode, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_channel`
GROUP BY 1, 2
HAVING n > 1;
```

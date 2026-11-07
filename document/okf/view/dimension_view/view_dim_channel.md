---
type: BigQuery View
title: "view_dim_channel"
description: "One row = one MAC5 department code (DepCode) of a company, with its sales, finance and cost channel mappings and their SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_channel&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_channel
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_channel.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_channel.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Combines [dim_channel](/dimension/dim_channel.md) with the three channel dimensions ([dim_channel_finance](/dimension/dim_channel_finance.md), [dim_channel_sales](/dimension/dim_channel_sales.md), [dim_channel_cost](/dimension/dim_channel_cost.md)) so that one row carries all four channel SKs (ChannelSK, ChannelFinanceSK, ChannelSaleSK, ChannelCostSK). The join keys are CompanySK + DepCode.

Read by: [export_view_dim_channel](/view/pub_sub/export_view_dim_channel.md), [fact_transcation](/fact/fact_transcation.md), [view_dim_aging](/view/dimension_view/view_dim_aging.md) and [view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md).

# Grain and key

One row = one department code of a company: key `companyID`, `DepCode` (unique; grain of dim_channel). The three LEFT JOINs match on the channel ID and CompanySK, so a channel with no entry in a child dimension has NULL for that SK.

# Schema

| Column | Type | Description |
|---|---|---|
| `ChannelSK` | INT64 | Stable SK of the row in [dim_channel](/dimension/dim_channel.md). |
| `ChannelFinanceSK` | INT64 | SK of the finance channel in dim_channel_finance matched on ChannelIDFinance + CompanySK; NULL if unmatched. |
| `ChannelSaleSK` | INT64 | SK of the sales channel in dim_channel_sales matched on ChannelID + CompanySK; NULL if unmatched. |
| `ChannelCostSK` | INT64 | SK of the cost channel in dim_channel_cost matched on ChannelCostID + CompanySK; NULL if unmatched. |
| `CompanySK` | INT64 | SK of the company in [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code. |
| `DepCode` | STRING | MAC5 department code (the join key to invoices/transactions, e.g. `mihDep`, `cfsDep`). |
| `DepGroup` | STRING | Department group code from dim_channel, e.g. `M35`, `MK4`, `HY`, `UB`. |
| `DepDesct` | STRING | Department description in Thai (pass-through from dim_channel). |
| `DepDesce` | STRING | Department description in English (pass-through from dim_channel). |
| `ChannelGroup` | STRING | Sales channel group name (pass-through from dim_channel). |
| `ChannelSubGroupName1` | STRING | Sales channel sub-group level 1 (pass-through). |
| `ChannelSubGroupName2` | STRING | Sales channel sub-group level 2 (pass-through). |
| `ChannelSubGroupName3` | STRING | Sales channel sub-group level 3 (pass-through). |
| `ChannelID` | STRING | Sales channel code (pass-through; join key to dim_channel_sales). |
| `ChannelName` | STRING | Sales channel name (pass-through). |
| `ChannelCostID` | STRING | Cost channel code (pass-through; join key to dim_channel_cost). |
| `ChannelCostName` | STRING | Cost channel name (pass-through). |
| `ChannelGroupFinance` | STRING | Finance channel group name (pass-through). |
| `ChannelSubGroupFinance1` | STRING | Finance channel sub-group level 1 (pass-through). |
| `ChannelSubGroupFinance2` | STRING | Finance channel sub-group level 2 (pass-through). |
| `ChannelSubGroupFinance3` | STRING | Finance channel sub-group level 3 (pass-through). |
| `ChannelIDFinance` | STRING | Finance channel code (pass-through; join key to dim_channel_finance). |
| `ChannelNameFinance` | STRING | Finance channel name (pass-through). |
| `ChannelDSite01` | STRING | Level 1 (site) of the D-channel hierarchy from dim_channel, e.g. `HO1`, `HY1`, `KTB`, `Other`. |
| `ChannelDDepartment02` | STRING | Level 2 (department) of the D-channel hierarchy from dim_channel, e.g. `SA`, `PD`, `SV`, `MK`, `Other`. |
| `ChannelDDivision03` | STRING | Level 3 (division) of the D-channel hierarchy from dim_channel, e.g. `SA_15`, `PD_10`, `Other`. |
| `ChannelDSubDivision04` | STRING | Level 4 (sub-division) of the D-channel hierarchy from dim_channel, e.g. `SA15_HP_N01`, `SA10_CEN`, `Other`. |
| `DummyChannel` | STRING | Dummy employee id from dim_channel (e.g. `9999991`) used in place of the line salesperson when matching sales representatives; `not calculated` when the department has none. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_channel.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_channel](/dimension/dim_channel.md), [dimension_table.dim_channel_finance](/dimension/dim_channel_finance.md), [dimension_table.dim_channel_sales](/dimension/dim_channel_sales.md), [dimension_table.dim_channel_cost](/dimension/dim_channel_cost.md).

# Examples

Channel mapping for one company:

```sql
SELECT DepCode, ChannelID, ChannelName, ChannelNameFinance, ChannelCostName
FROM `databuffet-nonprd.dimension_view.view_dim_channel`
WHERE companyID = 'ag01'
ORDER BY DepCode
```

Department codes without a sales-channel SK:

```sql
SELECT companyID, DepCode
FROM `databuffet-nonprd.dimension_view.view_dim_channel`
WHERE ChannelSaleSK IS NULL
```

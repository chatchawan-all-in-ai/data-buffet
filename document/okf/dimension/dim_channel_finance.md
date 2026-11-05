---
type: BigQuery Table
title: "dim_channel_finance"
description: "One row = one finance channel (code and name) per company, from the MDS finance-channel master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_channel_finance&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_channel_finance
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_channel_finance.sqlx"
    title: "Dataform definition (dimension/dim_channel_finance.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Lookup of finance channels; `ChannelIDFinance` is also a column of [dim_channel](/dimension/dim_channel.md). Source: mds `mds_data_channel_finance_master`.

Read by: [view_dim_channel](/view/dimension_view/view_dim_channel.md).

# Grain and key

One row = one finance channel of a company among active mds rows: key `ChannelFinanceSK` (surrogate, regenerated every run); natural key `companyID` + `ChannelIDFinance`.

# Schema

| Column | Type | Description |
|---|---|---|
| `ChannelFinanceSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY companyID, ChannelIDFinance)` over the active mds rows. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `ChannelIDFinance` | STRING | Pass-through of mds `ChannelIDFinance`, cleaned with `cleanString` (empty string becomes NULL). Natural key with companyID. |
| `ChannelNameFinance` | STRING | Pass-through of mds `ChannelNameFinance`, cleaned with `cleanString` (empty string becomes NULL). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_channel_finance_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_channel_finance.sqlx` (`type: "table"`, tag `dimension_daily`).
- `uniqueKey`: `ChannelFinanceSK`.
- Storage options: `{"clusterBy": ["ChannelFinanceSK"]}`.
- Reads: `mds_dataset.mds_data_channel_finance_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Codes and names for one company.

```sql
SELECT ChannelIDFinance, ChannelNameFinance
FROM `databuffet-nonprd.dimension_table.dim_channel_finance`
WHERE companyID = 'ag01'
ORDER BY ChannelIDFinance;
```

Duplicate natural keys.

```sql
SELECT companyID, ChannelIDFinance, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_channel_finance`
GROUP BY 1, 2
HAVING n > 1;
```

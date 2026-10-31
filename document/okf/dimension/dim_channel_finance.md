---
type: BigQuery Table
title: "dim_channel_finance"
description: "One row = one finance channel (code and name) per company, from the MDS finance-channel master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_channel_finance&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_channel_finance.sqlx"
    title: "Dataform definition (dimension/dim_channel_finance.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Lookup of finance channels. Consumed by [view_dim_channel](/view/dimension_view/view_dim_channel.md), which exposes the wide channel view together with [dim_channel](/dimension/dim_channel.md); `ChannelIDFinance` is also a column of dim_channel. Source: mds `mds_data_channel_finance_master`.

# Grain and key

One row per (company, ChannelIDFinance) among active mds rows. Key: `ChannelFinanceSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `ChannelFinanceSK` | INT64 | `ChannelFinanceSK` is `ROW_NUMBER() OVER(ORDER BY companyID, ChannelIDFinance)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `ChannelIDFinance` | STRING | Pass-through of mds `ChannelIDFinance`, cleaned with `cleanString` (empty string becomes NULL). Natural key with companyID. |
| `ChannelNameFinance` | STRING | Pass-through of mds `ChannelNameFinance`, cleaned with `cleanString` (empty string becomes NULL). |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_channel_finance.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `ChannelFinanceSK`.
- Storage options: `{"clusterBy": ["ChannelFinanceSK"]}`.
- Reads: `mds_dataset.mds_data_channel_finance_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows (`is_active = TRUE`); runs after dim_company (declared dependency).
- Approximate size (BigQuery metadata, 2026-10-31): 188 rows, 18.7 KB.

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

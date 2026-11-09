---
type: BigQuery Table
title: "dim_price_channel"
description: "One row = one D-ERP sales channel, with source hierarchy and parent channel key."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_price_channel&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_price_channel
tags: ["dimension", "derp", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_price_channel.sqlx"
    title: "Dataform definition (dimension/dim_price_channel.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:codex", at: "2026-11-09T11:36:30+07:00" }
status: draft
---

# What it is

D-ERP sales-channel master with the source hierarchy and a self-lookup parent key. This source is separate from the MDS channel dimension and has no relationship to `view_dim_channel`. `CompanySK` is populated only when the source `CompanyCode` maps to one company in [dim_company](dim_company.md).

# Grain and key

One row = one `master_sales_channel_id`. Natural key: `MasterSalesChannelID`. `PriceChannelSK` is retained for a matching natural key and new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed. `ParentPriceChannelSK` looks up `ParentID` within the same complete source snapshot.

# Schema

| Column | Type | Description |
|---|---|---|
| `PriceChannelSK` | INT64 | Stable surrogate key for `MasterSalesChannelID`. |
| `MasterSalesChannelID` | STRING | D-ERP sales-channel identifier; natural key. |
| `SalesChannelCode` | STRING | Source sales-channel code. |
| `SalesChannelName` | STRING | Source sales-channel name. |
| `Description` | STRING | Source sales-channel description. |
| `Status` | STRING | Source sales-channel status. |
| `Level` | INT64 | Source hierarchy level. |
| `OrderSort` | INT64 | Source order for displaying channels. |
| `ParentID` | STRING | Source parent channel identifier. |
| `ParentPriceChannelSK` | INT64 | Parent key looked up from `ParentID` within this dimension; NULL when the source has no parent. |
| `PathID` | STRING | Source hierarchy path identifier. |
| `PathCode` | STRING | Source hierarchy path code. |
| `PathName` | STRING | Source hierarchy path name. |
| `CompanyCode` | STRING | Source company code. |
| `OrganizationCode` | STRING | Source organization code. |
| `CompanySK` | INT64 | Nullable company key; populated only for one matching `dim_company.CompanyCode`. |
| `SourceUpdatedAt` | DATETIME | Source `updated_at`. |
| `SourceAsatdate` | DATE | Source snapshot date. |
| `asatdate` | DATE | Bangkok date on which the dimension action runs. |

# How it is built

- Definition: `definitions/dimension/dim_price_channel.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`).
- Reads the complete `${ref(databuffet.VALIDATED_DERP, "sales_channel_master_sales_channel")}` snapshot and depends on [dim_company](dim_company.md).
- Resolves `CompanySK` only for a unique source `CompanyCode` match. Resolves `ParentPriceChannelSK` from the channel IDs in the same snapshot.
- Synchronizes by `MasterSalesChannelID`: matching rows keep `PriceChannelSK`, new rows receive `MAX(PriceChannelSK) + ROW_NUMBER()`, and missing source rows are deleted.

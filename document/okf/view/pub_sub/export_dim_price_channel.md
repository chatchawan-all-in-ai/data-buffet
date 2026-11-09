---
type: BigQuery View
title: "export_dim_price_channel"
description: "One row = one D-ERP sales channel, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_price_channel&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_price_channel
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_price_channel.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_price_channel.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:codex", at: "2026-11-09T14:42:36+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_price_channel](/dimension/dim_price_channel.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_price_channel`.

# Grain and key

One row = one D-ERP sales channel. Natural key: `MasterSalesChannelID`; `row_key` is the JSON of that key.

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
| `row_key` | STRING | JSON of `MasterSalesChannelID`, used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of all 19 data columns, i.e. exactly the message `data`. |

# Price joins

This export carries the independent sales-channel hierarchy. Price-sheet joins by `ProductSK` and `CompanySK`, including ambiguous or unmatched products, follow the [dim_price mapping contract](/dimension/dim_price.md).

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_price_channel.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_price_channel](/dimension/dim_price_channel.md).

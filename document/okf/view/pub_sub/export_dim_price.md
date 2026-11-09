---
type: BigQuery View
title: "export_dim_price"
description: "One row = one D-ERP price sheet, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_price&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_price
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_price.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_price.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:codex", at: "2026-11-09T14:42:36+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_price](/dimension/dim_price.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_price`.

# Grain and key

One row = one D-ERP price sheet. Natural key: `NdSdPriceID`; `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `PriceSK` | INT64 | Stable surrogate key for `NdSdPriceID`. |
| `NdSdPriceID` | STRING | D-ERP price-sheet identifier; natural key. |
| `ProductID` | STRING | Product identifier from the price sheet. |
| `ProductCode` | STRING | Product code from the price sheet. |
| `ProductBarcode` | STRING | Product barcode from the price sheet. |
| `ProductSK` | INT64 | Stable product key for a unique ag01 `ProductCode` match; NULL when unmatched or ambiguous. |
| `CompanySK` | INT64 | Stable company key for ag01, the known D-ERP source scope. |
| `ProductMatchCount` | INT64 | Number of ag01 product rows matching the lower-cased `ProductCode`; zero means unmatched. |
| `CompanyResolutionStatus` | STRING | `RESOLVED` for the asserted ag01 company mapping. |
| `ProductResolutionStatus` | STRING | `RESOLVED` for one match, `AMBIGUOUS` for multiple matches, or `UNMATCHED` for no match. |
| `EffectiveFrom` | DATE | First date the source sheet is effective. |
| `ExpiryTo` | DATE | Last effective date; NULL remains NULL. |
| `Status` | STRING | Source sheet status; all source statuses are retained. |
| `ListPriceInclVat` | FLOAT64 | Source `list_price_incl_vat`. |
| `ListPriceExclVat` | FLOAT64 | Source `list_price_excl_vat`; kept as supplied. |
| `ListPriceVatRate` | FLOAT64 | Source `list_price_vat_rate`; kept as supplied. |
| `FloorPct` | FLOAT64 | Source floor percentage or amount. |
| `FloorPriceInclVat` | FLOAT64 | Source floor price inclusive of VAT. |
| `FloorRateType` | STRING | Source floor rule type. |
| `NdMinQty` | INT64 | Source ND minimum quantity. |
| `NdMaxQty` | INT64 | Source ND maximum quantity. |
| `Remark` | STRING | Source price-sheet remark. |
| `SourceUpdatedAt` | DATETIME | Source `updated_at`. |
| `SourceDeletedAt` | DATETIME | Source `deleted_at`. |
| `SourceAsatdate` | DATE | Source snapshot date. |
| `asatdate` | DATE | Bangkok date on which the dimension action runs. |
| `row_key` | STRING | JSON of `NdSdPriceID`, used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of all 26 data columns, i.e. exactly the message `data`. |

# Price joins

For joins by `ProductSK` and `CompanySK`, including NULL keys for ambiguous or unmatched products, see the [dim_price mapping contract](/dimension/dim_price.md) and [tier lookup example](/dimension/dim_price_tier.md#examples). The tier relationship is exposed by [export_dim_price_tier](/view/pub_sub/export_dim_price_tier.md).

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_price.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_price](/dimension/dim_price.md).

---
type: BigQuery View
title: "export_dim_price_tier"
description: "One row = one ND, SD1, SD2, SD3 or BIGPRO tier of a D-ERP price sheet, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_price_tier&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_price_tier
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_price_tier.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_price_tier.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:codex", at: "2026-11-09T14:42:36+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_price_tier](/dimension/dim_price_tier.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_price_tier`.

# Grain and key

One row = one (`NdSdPriceID`, `TierCode`) pair. Natural key: (`NdSdPriceID`, `TierCode`); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `PriceTierSK` | INT64 | Stable surrogate key for a price-sheet tier. |
| `PriceSK` | INT64 | Parent key from [dim_price](/dimension/dim_price.md), joined by `NdSdPriceID`. |
| `NdSdPriceID` | STRING | D-ERP price-sheet identifier. |
| `TierCode` | STRING | Tier name: `ND`, `SD1`, `SD2`, `SD3` or `BIGPRO`. |
| `MinQty` | INT64 | Tier minimum quantity; source value. |
| `MaxQty` | INT64 | Tier maximum quantity; source value. |
| `Rate` | FLOAT64 | SD or BIGPRO source rate; NULL for ND. |
| `RateType` | STRING | SD or BIGPRO source rate type; NULL for ND. |
| `PriceInclVat` | FLOAT64 | ND `list_price_incl_vat`; NULL for SD and BIGPRO. |
| `PriceExclVat` | FLOAT64 | ND `list_price_excl_vat`, or the SD/BIGPRO source `*_price_excl_vat`. |
| `VatRate` | FLOAT64 | ND `list_price_vat_rate`; NULL for SD and BIGPRO. |
| `VatBasisStatus` | STRING | `missing` when both source price fields are NULL; otherwise `unverified`. |
| `QuantityRuleStatus` | STRING | `confirmed` when `MinQty` is present, `unverified` when only `MaxQty` is present, and `missing` when no range is supplied, including BIGPRO. |
| `SourceAsatdate` | DATE | Source snapshot date. |
| `asatdate` | DATE | Bangkok date on which the dimension action runs. |
| `row_key` | STRING | JSON of `NdSdPriceID` and `TierCode`, used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of all 15 data columns, i.e. exactly the message `data`. |

# Price joins

Join this tier view to [export_dim_price](/view/pub_sub/export_dim_price.md) by `PriceSK` or `NdSdPriceID`. For the parent’s `ProductSK` and `CompanySK` joins and ambiguous or unmatched products, see the [dim_price mapping contract](/dimension/dim_price.md) and [tier lookup example](/dimension/dim_price_tier.md#examples).

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_price_tier.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_price_tier](/dimension/dim_price_tier.md).

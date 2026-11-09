---
type: BigQuery Table
title: "dim_price"
description: "One row = one D-ERP ND/SD price sheet, with source identity, validity, status, floor and quantity attributes."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_price&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_price
tags: ["dimension", "derp", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_price.sqlx"
    title: "Dataform definition (dimension/dim_price.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:codex", at: "2026-11-09T11:52:48+07:00" }
status: draft
---

# What it is

D-ERP price-sheet header and base ND price attributes intended for lookup from `fact_order`, `fact_quotation` and `view_fact_transcation` by `ProductSK` and document date. The source has no company and its `product_barcode` is empty. The current action always writes NULL to `ProductSK`, `CompanySK` and `ProductMatchCount`, and `UNKNOWN` to both resolution statuses; it does not implement company or product matching. The source `Status` is retained without filtering. See the [order-quantity lookup example](dim_price_tier.md#examples) for the selection rule and current mapping limitation.

Read by: [dim_price_tier](dim_price_tier.md).

# Grain and key

One row = one `nd_sd_price_id`. Natural key: `NdSdPriceID`. `PriceSK` is retained for a matching natural key and new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `PriceSK` | INT64 | Stable surrogate key for `NdSdPriceID`. |
| `NdSdPriceID` | STRING | D-ERP price-sheet identifier; natural key. |
| `ProductID` | STRING | Product identifier from the price sheet. |
| `ProductCode` | STRING | Product code from the price sheet. |
| `ProductBarcode` | STRING | Product barcode from the price sheet. |
| `ProductSK` | INT64 | Product key placeholder; always NULL in the current action. |
| `CompanySK` | INT64 | Company key placeholder; always NULL in the current action. |
| `ProductMatchCount` | INT64 | Candidate-count placeholder; always NULL in the current action. |
| `CompanyResolutionStatus` | STRING | Company mapping state; always `UNKNOWN` in the current action. |
| `ProductResolutionStatus` | STRING | Product mapping state; always `UNKNOWN` in the current action. |
| `EffectiveFrom` | DATE | First date the source sheet is effective. |
| `ExpiryTo` | DATE | Last effective date; NULL remains NULL. |
| `Status` | STRING | Source sheet status; all source statuses are retained. |
| `ListPriceInclVat` | FLOAT64 | Source `list_price_incl_vat`. |
| `ListPriceExclVat` | FLOAT64 | Source `list_price_excl_vat`; kept as supplied. |
| `ListPriceVatRate` | FLOAT64 | Source `list_price_vat_rate`; kept as supplied. |
| `FloorPct` | FLOAT64 | Source floor percentage or amount. |
| `FloorPriceInclVat` | FLOAT64 | Source floor price inclusive of VAT. |
| `FloorRateType` | STRING | Source floor rule type; `percent` means list price × `FloorPct` / 100, and `bath` means list price − `FloorPct`. |
| `NdMinQty` | INT64 | Source ND minimum quantity. |
| `NdMaxQty` | INT64 | Source ND maximum quantity. |
| `Remark` | STRING | Source price-sheet remark. |
| `SourceUpdatedAt` | DATETIME | Source `updated_at`. |
| `SourceDeletedAt` | DATETIME | Source `deleted_at`. |
| `SourceAsatdate` | DATE | Source snapshot date. |
| `asatdate` | DATE | Bangkok date on which the dimension action runs. |

# How it is built

- Definition: `definitions/dimension/dim_price.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`).
- Reads the complete `${ref(databuffet.VALIDATED_DERP, "crm_nd_sd_price")}` snapshot and retains every source `Status`.
- No company is inferred from product codes. `ListPriceExclVat` and `ListPriceVatRate` stay as source values; no VAT value is filled.
- Synchronizes by `NdSdPriceID`: matching rows keep `PriceSK`, new rows receive `MAX(PriceSK) + ROW_NUMBER()`, and missing source rows are deleted.

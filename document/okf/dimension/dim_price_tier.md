---
type: BigQuery Table
title: "dim_price_tier"
description: "One row = one ND, SD1, SD2, SD3 or BIGPRO tier for a D-ERP price sheet."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_price_tier&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_price_tier
tags: ["dimension", "derp", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_price_tier.sqlx"
    title: "Dataform definition (dimension/dim_price_tier.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:codex", at: "2026-11-09T11:52:48+07:00" }
status: draft
---

# What it is

The ND, SD1, SD2, SD3 and BIGPRO tiers unpivoted from each D-ERP price sheet. `PriceSK` links to [dim_price](dim_price.md). Empty price fields are not eligible prices. VAT basis is `unverified` when a tier has a source price and `missing` when both source price fields are empty. Quantity rule status is `confirmed` when `MinQty` is present, `unverified` when only `MaxQty` is present, and `missing` when no usable range is supplied; BIGPRO has no quantity range.

# Grain and key

One row = one (`NdSdPriceID`, `TierCode`) pair. `TierCode` is one of `ND`, `SD1`, `SD2`, `SD3` or `BIGPRO`. Natural key: (`NdSdPriceID`, `TierCode`). `PriceTierSK` is retained for a matching natural key and new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `PriceTierSK` | INT64 | Stable surrogate key for a price-sheet tier. |
| `PriceSK` | INT64 | Parent key from [dim_price](dim_price.md), joined by `NdSdPriceID`. |
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

# How it is built

- Definition: `definitions/dimension/dim_price_tier.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`).
- Reads the complete `${ref(databuffet.VALIDATED_DERP, "crm_nd_sd_price")}` snapshot and depends on [dim_price](dim_price.md).
- Creates all five tier rows for every source price sheet, including tiers whose source price or quantity fields are NULL. BIGPRO has no quantity bounds and cannot match a quantity range.
- Synchronizes by (`NdSdPriceID`, `TierCode`): matching rows keep `PriceTierSK`, new rows receive `MAX(PriceTierSK) + ROW_NUMBER()`, and missing source rows are deleted.

# Examples

Sum paid PS order-line quantity for each company, order and product before selecting a price sheet effective on the order document date and its tier.

```sql
WITH order_product_quantity AS (
  SELECT
    company_id,
    milVnos,
    milStk,
    SUM(milQuan) AS TotalQty
  FROM `databuffet-nonprd.curated_mac5.curated_mil`
  WHERE milType = 'PS'
    AND milUprice > 0
  GROUP BY company_id, milVnos, milStk
), order_product AS (
  SELECT
    q.company_id,
    q.milVnos,
    q.milStk,
    product.ProductSK,
    PARSE_DATE('%Y%m%d', CONCAT(
      header.mihYear, FORMAT('%02d', header.mihMonth), FORMAT('%02d', header.mihDay)
    )) AS DocumentDate,
    q.TotalQty
  FROM order_product_quantity AS q
  JOIN `databuffet-nonprd.curated_mac5.curated_mih` AS header
    ON header.company_id = q.company_id
    AND header.mihType = 'PS'
    AND header.mihVnos = q.milVnos
  JOIN `databuffet-nonprd.dimension_table.dim_product_master` AS product
    ON product.companyID = q.company_id
    AND LOWER(product.ProductCode) = LOWER(q.milStk)
)
SELECT
  q.company_id,
  q.milVnos,
  q.milStk,
  q.ProductSK,
  q.DocumentDate,
  q.TotalQty,
  p.PriceSK,
  tier.PriceTierSK,
  tier.TierCode,
  tier.PriceInclVat,
  tier.PriceExclVat
FROM order_product AS q
JOIN `databuffet-nonprd.dimension_table.dim_price` AS p
  ON p.ProductSK = q.ProductSK
  AND q.DocumentDate BETWEEN p.EffectiveFrom AND IFNULL(p.ExpiryTo, DATE '9999-12-31')
  AND p.Status = 'ACTIVE'
JOIN `databuffet-nonprd.dimension_table.dim_price_tier` AS tier
  ON tier.PriceSK = p.PriceSK
  AND tier.MinQty <= q.TotalQty
  AND q.TotalQty <= IFNULL(tier.MaxQty, 9223372036854775807)
  AND COALESCE(tier.PriceInclVat, tier.PriceExclVat) IS NOT NULL;
```

The quantity is summed from `curated_mac5.curated_mil` PS lines with `milUprice > 0`, grouped by `company_id`, `milVnos` and `milStk`, before any dimension joins. Resolve `ProductSK` by company and product code, and use the PS header date from `curated_mac5.curated_mih` for price validity; partial billings and their dates do not change the order quantity or date used here. Match the price sheet by `ProductSK` and order document date, then apply the quantity range. This lookup reads NULL `MaxQty` as no upper bound, pending confirmation from D-ERP. BIGPRO has no `MinQty`, so it does not match this quantity-range lookup. An empty tier price is not eligible. Price sheets currently have NULL `ProductSK`, so this lookup returns no matches until company-confirmed product mapping is available.

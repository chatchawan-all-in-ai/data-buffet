---
type: BigQuery Table
title: "crm_nd_sd_price"
description: "One row = one ND/SD price record for a product from source table `crm_nd_sd_price`, unique on (nd_sd_price_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_nd_sd_price&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_nd_sd_price
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_nd_sd_price.sqlx"
    title: "Dataform definition (validated/derp/crm_nd_sd_price.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_nd_sd_price`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product selling prices with list price, floor price, the normal-discount (ND) quantity tier and up to three special-discount (SD) tiers.
Read by: [dim_price](../../dimension/dim_price.md) and [dim_price_tier](../../dimension/dim_price_tier.md).

# Grain and key

One row per `nd_sd_price_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `nd_sd_price_id` | STRING | UUID of the ND/SD price record. |
| `product_id` | STRING | UUID of the product in the DERP product master. |
| `product_code` | STRING | Product (item) code. |
| `product_barcode` | STRING | Product barcode. |
| `effective_from` | DATE | Date the price takes effect. |
| `expiry_to` | DATE | Date the price expires (NULL = open-ended). |
| `status` | STRING | Price record status (`ACTIVE`, `INACTIVE` or `DELETE`). |
| `list_price_incl_vat` | FLOAT64 | List price including VAT, in THB. |
| `list_price_excl_vat` | FLOAT64 | List price excluding VAT, in THB. |
| `list_price_vat_rate` | FLOAT64 | VAT rate used for the list price, in percent. |
| `floor_pct` | FLOAT64 | Floor price as a percentage of the list price. |
| `floor_price_incl_vat` | FLOAT64 | Floor (minimum allowed) price including VAT, in THB. |
| `nd_min_qty` | INT64 | Minimum quantity for the ND (normal discount) price tier. |
| `nd_max_qty` | INT64 | Maximum quantity for the ND (normal discount) price tier. |
| `sd1_rate` | FLOAT64 | Discount rate of special-discount tier 1, in the unit given by `sd1_rate_type`. |
| `sd1_rate_type` | STRING | Unit of the tier-1 discount rate (`percent` or `bath` = THB amount). |
| `sd1_price_excl_vat` | FLOAT64 | Unit price excluding VAT for special-discount tier 1, in THB. |
| `sd1_min_qty` | INT64 | Minimum quantity for special-discount tier 1. |
| `sd1_max_qty` | INT64 | Maximum quantity for special-discount tier 1. |
| `sd2_rate` | FLOAT64 | Discount rate of special-discount tier 2, in the unit given by `sd2_rate_type`. |
| `sd2_rate_type` | STRING | Unit of the tier-2 discount rate (`percent` or `bath` = THB amount). |
| `sd2_price_excl_vat` | FLOAT64 | Unit price excluding VAT for special-discount tier 2, in THB. |
| `sd2_min_qty` | INT64 | Minimum quantity for special-discount tier 2. |
| `sd2_max_qty` | INT64 | Maximum quantity for special-discount tier 2. |
| `sd3_rate` | FLOAT64 | Discount rate of special-discount tier 3, in the unit given by `sd3_rate_type`. |
| `sd3_rate_type` | STRING | Unit of the tier-3 discount rate (`percent` or `bath` = THB amount). |
| `sd3_price_excl_vat` | FLOAT64 | Unit price excluding VAT for special-discount tier 3, in THB. |
| `sd3_min_qty` | INT64 | Minimum quantity for special-discount tier 3. |
| `sd3_max_qty` | INT64 | Maximum quantity for special-discount tier 3. |
| `bigpro_rate` | FLOAT64 | Discount rate of the big-promotion price, in the unit given by `bigpro_rate_type`. |
| `bigpro_rate_type` | STRING | Unit of the big-promotion discount rate (`percent` or `bath` = THB amount). |
| `bigpro_price_excl_vat` | FLOAT64 | Big-promotion unit price excluding VAT, in THB. |
| `remark` | STRING | Free-text remark on the price. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `deleted_at` | DATETIME | Timestamp when the record was soft-deleted (NULL while active). |
| `floor_rate_type` | STRING | Unit of the floor rate (`percent` or `bath` = THB amount). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_nd_sd_price.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_nd_sd_price](/initial/raw_derp/crm_nd_sd_price.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `nd_sd_price_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_nd_sd_price`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT nd_sd_price_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_nd_sd_price`
GROUP BY nd_sd_price_id
HAVING n > 1
```

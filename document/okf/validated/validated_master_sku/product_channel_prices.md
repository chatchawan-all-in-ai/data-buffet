---
type: BigQuery Table
title: "product_channel_prices"
description: "One row per `product_channel_prices` from source table `product_channel_prices`, unique on (product_id, sales_channel_id, business_unit_id, effective_date)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=product_channel_prices&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: product_channel_prices
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/product_channel_prices.sqlx"
    title: "Dataform definition (validated/master_sku/product_channel_prices.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki: validated layer"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T22:49:49+07:00" }
status: draft
---



# What it is

Validated copy of MASTER_SKU `product_channel_prices`: string values are cleaned, numeric values are typed and UTC datetimes are converted to Bangkok DATETIME values, the extract date is standardised to `asatdate`, and duplicate keys are collapsed. Table meaning: product prices by sales channel, business unit, and effective date.

# Grain and key

One row per (product_id, sales_channel_id, business_unit_id, effective_date). The composite key is declared in `uniqueKey` and `pk_key`; the definition adds it as a `NOT ENFORCED` primary key after a full build.

# Schema

| Column | Type | Description |
|---|---|---|
| `product_id` | STRING | Product identifier. |
| `sales_channel_id` | STRING | Sales channel identifier. |
| `business_unit_id` | STRING | Business unit identifier; nullable in the source. |
| `normal_discount_percent` | INT64 | Normal discount percent. |
| `special_discount_percent_1` | INT64 | First special discount percent. |
| `special_discount_percent_2` | INT64 | Second special discount percent. |
| `special_discount_percent_3` | INT64 | Third special discount percent. |
| `minimum_price` | FLOAT64 | Minimum price. |
| `minimum_discount` | FLOAT64 | Minimum discount. |
| `marketing_price` | FLOAT64 | Marketing price. |
| `effective_date` | STRING | Price effective date. |
| `expiration_date` | STRING | Price expiration date. |
| `status` | STRING | Source status. |
| `created_at` | DATETIME | Creation datetime converted from UTC to Asia/Bangkok. |
| `created_by` | STRING | Creator identifier. |
| `updated_at` | DATETIME | Update datetime converted from UTC to Asia/Bangkok. |
| `updated_by` | STRING | Updater identifier. |
| `asatdate` | DATE | Extract date parsed from the raw ASATDATE partition. |

# How it is built

- Definition: `definitions/validated/master_sku/product_channel_prices.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.product_channel_prices](../../initial/raw_master_sku/product_channel_prices.md).
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY product_id, sales_channel_id, business_unit_id, effective_date ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by product_id, sales_channel_id, business_unit_id, effective_date.

# Examples

Recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.product_channel_prices`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

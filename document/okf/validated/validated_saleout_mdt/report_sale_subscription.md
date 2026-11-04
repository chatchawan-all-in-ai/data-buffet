---
type: BigQuery Table
title: "report_sale_subscription"
description: "One row = one SKU at one Thai Watsadu branch in one daily file from source table `report_sale_subscription` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=report_sale_subscription&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: report_sale_subscription
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_full", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/TW/report_sale_subscription.sqlx"
    title: "Dataform definition (validated/saleout_mdt/TW/report_sale_subscription.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of SALEOUT_MDT `report_sale_subscription`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Daily Thai Watsadu (TW) sales-and-stock report for the company products: sales on the last sold date, stock on hand and on order per branch and SKU.
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [curated_saleout_mdt.curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md).

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `Store` | STRING | Thai Watsadu branch as code plus name (e.g. `60001-CRC Thai Watsadu ...`), used as the branch code. |
| `Cat` | STRING | Thai Watsadu category code (e.g. `002`). |
| `Sub_Cat` | STRING | Thai Watsadu sub-category code (e.g. `004`). |
| `Brand` | STRING | Product brand. |
| `SKU` | STRING | Thai Watsadu SKU (zero-padded). |
| `Barcode` | STRING | Product barcode (EAN-13). |
| `Description` | STRING | Product description (name). |
| `Product_Type` | STRING | Stock location type of the row (e.g. `Branch`). |
| `Sales_Amount` | FLOAT64 | Sales amount of the SKU at the branch (THB). |
| `Sales_Qty` | INT64 | Sales quantity of the SKU at the branch. |
| `Stock_On_Hand` | FLOAT64 | Stock quantity on hand at the branch. |
| `Stock_On_Order` | INT64 | Stock quantity on open purchase orders. |
| `Last_Sold_Date` | DATE | Date the SKU was last sold at the branch. |
| `Last_Receive_Date` | DATE | Date the SKU was last received at the branch. |
| `ASATDATE` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/TW/report_sale_subscription.sqlx` (`type: "table"`, tags `validated`, `validated_full`, `saleout_daily`).
- Reads: [raw_saleout_mdt.report_sale_subscription](/initial/raw_saleout_mdt/report_sale_subscription.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `asatdate`, cluster by `Store`, `SKU`, `Last_Sold_Date`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.report_sale_subscription`
LIMIT 100
```

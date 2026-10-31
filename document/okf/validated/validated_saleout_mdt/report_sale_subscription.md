---
type: BigQuery Table
title: "report_sale_subscription"
description: "One row = one cleaned source record of `report_sale_subscription` (no declared key; append-style, not deduplicated)."
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

Validated copy of SALEOUT_MDT `report_sale_subscription`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [curated_saleout_mdt.curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md).

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `Store` | STRING | Meaning not documented in the repo. |
| `Cat` | STRING | Meaning not documented in the repo. |
| `Sub_Cat` | STRING | Meaning not documented in the repo. |
| `Brand` | STRING | Meaning not documented in the repo. |
| `SKU` | STRING | Meaning not documented in the repo. |
| `Barcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `Description` | STRING | Meaning not documented in the repo. |
| `Product_Type` | STRING | Meaning not documented in the repo. |
| `Sales_Amount` | FLOAT64 | Meaning not documented in the repo. |
| `Sales_Qty` | INT64 | Meaning not documented in the repo. |
| `Stock_On_Hand` | FLOAT64 | Meaning not documented in the repo. |
| `Stock_On_Order` | INT64 | Meaning not documented in the repo. |
| `Last_Sold_Date` | DATE | Meaning not documented in the repo. |
| `Last_Receive_Date` | DATE | Meaning not documented in the repo. |
| `ASATDATE` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/TW/report_sale_subscription.sqlx` (`type: "table"`, tags `validated`, `validated_full`, `saleout_daily`).
- Reads: [raw_saleout_mdt.report_sale_subscription](/initial/raw_saleout_mdt/report_sale_subscription.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `asatdate`, cluster by `Store`, `SKU`, `Last_Sold_Date`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,900,208 rows, 459.3 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.report_sale_subscription`
LIMIT 100
```

---
type: BigQuery Table
title: "stock_aging"
description: "One row per (vendor_id, branch, article_id, aging_tier, brand, mch3, mch2, end_date, asatdate) after SQL deduplication; fully rebuilt, with arbitrary selection among tied source records."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=stock_aging&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: stock_aging
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_full", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/BT/stock_aging.sqlx"
    title: "Dataform definition (validated/saleout_mdt/BT/stock_aging.sqlx)"
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

Validated copy of SALEOUT_MDT `stock_aging`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Stock aging report from Boonthavorn (BT): stock quantity and value of the company products by branch, article and age band, with stock class.
No other table or view in this repository reads it.

# Grain and key

One row per cleaned tuple `(vendor_id, branch, article_id, aging_tier, brand, mch3, mch2, end_date, asatdate)`, selected by `QUALIFY ROW_NUMBER() = 1`. There is no declared `uniqueKey` or primary-key constraint, but SQL still deduplicates. `ORDER BY asatdate` is constant within each partition because asatdate is also in the tuple; records with that same tuple are tied, so the retained row is arbitrary when other attributes or quantities differ. Different extract dates remain separate snapshots.

# Schema

| Column | Type | Description |
|---|---|---|
| `vendor_id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `vendor_name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `branch` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `article_id` | STRING | Boonthavorn article (product) code. |
| `article_name_th` | STRING | Product name in Thai. |
| `brand` | STRING | Product brand. |
| `mch3` | STRING | Boonthavorn merchandise category, top level (department). |
| `mch2` | STRING | Boonthavorn merchandise category, second level. |
| `tile_size` | FLOAT64 | Tile size of the article (tile products only). |
| `item_flag` | STRING | Item movement flag (`REGULAR`, `FAST`, `DISCON` = discontinued). |
| `aging_tier` | STRING | Stock age band (`1) 0 - 60 Days` to `8) >361 Days`). |
| `class_stock` | STRING | Boonthavorn stock class (`B3G Class A`, `B3G Class B`, `B3G Class C`, `B3G New`, `B3G Dead`). |
| `aging` | INT64 | Stock age in days. |
| `ur_amt` | FLOAT64 | Value of the unrestricted stock in this age band (THB). |
| `ur_qty` | INT64 | Unrestricted stock quantity in this age band. |
| `reserve_amt` | FLOAT64 | Value of the stock reserved for orders (THB). |
| `reserve_qty` | INT64 | Stock quantity reserved for orders. |
| `remain_amt` | FLOAT64 | Value of the stock remaining after reservations (THB). |
| `remain_qty` | INT64 | Stock quantity remaining after reservations. |
| `start_date` | DATE | Stock snapshot date (same as `end_date`). |
| `end_date` | DATE | Stock snapshot date. |
| `ASATDATE` | DATE | Extract date (raw ASATDATE parsed to DATE); part of the deduplication tuple and the storage partition. It does not break ties within the tuple. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/stock_aging.sqlx` (`type: "table"`, tags `validated`, `validated_full`, `saleout_daily`).
- Reads: [raw_saleout_mdt.stock_aging](/initial/raw_saleout_mdt/stock_aging.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `asatdate`, cluster by `branch`, `article_id`, `aging_tier`.
- Approximate size (BigQuery metadata, 2026-10-31): 45,231 rows, 14.9 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.stock_aging`
LIMIT 100
```

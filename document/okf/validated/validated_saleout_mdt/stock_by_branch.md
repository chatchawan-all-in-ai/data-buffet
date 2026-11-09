---
type: BigQuery Table
title: "stock_by_branch"
description: "One row per (vendor_id, branch, article_id, end_date, asatdate) after SQL deduplication; fully rebuilt, with arbitrary selection among tied source records."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=stock_by_branch&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: stock_by_branch
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_full", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/BT/stock_by_branch.sqlx"
    title: "Dataform definition (validated/saleout_mdt/BT/stock_by_branch.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-09T02:15:58+00:00" }
status: draft
---

# What it is

Validated copy of SALEOUT_MDT `stock_by_branch`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Daily on-hand stock (quantity and cost value) of the company products at each Boonthavorn (BT) branch.

Read by: [curated_saleout_mdt.curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md).

# Grain and key

One row per cleaned tuple `(vendor_id, branch, article_id, end_date, asatdate)`, selected by `QUALIFY ROW_NUMBER() = 1`. `uniqueKey` and `pk_key` declare this tuple; each full rebuild attaches a `NOT ENFORCED` primary key using the standard retry loop. `ORDER BY asatdate` is constant within each partition because asatdate is also in the tuple; records with that same tuple are tied, so the retained row is arbitrary when other attributes or quantities differ. Different extract dates remain separate snapshots.

# Schema

| Column | Type | Description |
|---|---|---|
| `vendor_id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `vendor_name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `branch` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `mch3` | STRING | Boonthavorn merchandise category, top level (department). |
| `article_id` | STRING | Boonthavorn article (product) code. |
| `article_name_th` | STRING | Product name in Thai. |
| `item_flag` | STRING | Item movement flag (`REGULAR`, `FAST`, `DISCON` = discontinued). |
| `ur_qty` | INT64 | Unrestricted (available) stock quantity on hand. |
| `ur_cost_amt` | FLOAT64 | Value of the unrestricted stock at cost (THB). |
| `start_date` | DATE | Stock snapshot date (same as `end_date`). |
| `end_date` | DATE | Stock snapshot date. |
| `asatdate` | DATE | Extract date (raw ASATDATE parsed to DATE); part of the deduplication tuple and the storage partition. It does not break ties within the tuple. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/stock_by_branch.sqlx` (`type: "table"`, tags `validated`, `validated_full`, `saleout_daily`).
- Reads: [raw_saleout_mdt.stock_by_branch](/initial/raw_saleout_mdt/stock_by_branch.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `asatdate`, cluster by `branch`, `article_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.stock_by_branch`
LIMIT 100
```

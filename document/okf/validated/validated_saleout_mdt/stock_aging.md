---
type: BigQuery Table
title: "stock_aging"
description: "One row per (vendor_id, branch, article_id, aging_tier, brand, mch3, mch2, end_date, asatdate) after SQL deduplication; fully rebuilt, with arbitrary selection among tied source records."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=stock_aging&page=table"
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

Validated copy of SALEOUT_MDT `stock_aging`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per cleaned tuple `(vendor_id, branch, article_id, aging_tier, brand, mch3, mch2, end_date, asatdate)`, selected by `QUALIFY ROW_NUMBER() = 1`. There is no declared `uniqueKey` or primary-key constraint, but SQL still deduplicates. `ORDER BY asatdate` is constant within each partition because asatdate is also in the tuple; records with that same tuple are tied, so the retained row is arbitrary when other attributes or quantities differ. Different extract dates remain separate snapshots.

# Schema

| Column | Type | Description |
|---|---|---|
| `vendor_id` | STRING | Meaning not documented in the repo. |
| `vendor_name` | STRING | Meaning not documented in the repo. |
| `branch` | STRING | Meaning not documented in the repo. |
| `article_id` | STRING | Meaning not documented in the repo. |
| `article_name_th` | STRING | Meaning not documented in the repo. |
| `brand` | STRING | Meaning not documented in the repo. |
| `mch3` | STRING | Meaning not documented in the repo. |
| `mch2` | STRING | Meaning not documented in the repo. |
| `tile_size` | FLOAT64 | Meaning not documented in the repo. |
| `item_flag` | STRING | Meaning not documented in the repo. |
| `aging_tier` | STRING | Meaning not documented in the repo. |
| `class_stock` | STRING | Meaning not documented in the repo. |
| `aging` | INT64 | Meaning not documented in the repo. |
| `ur_amt` | FLOAT64 | Likely amount (inferred from the column name only; not documented in the repo). |
| `ur_qty` | INT64 | Likely quantity (inferred from the column name only; not documented in the repo). |
| `reserve_amt` | FLOAT64 | Meaning not documented in the repo. |
| `reserve_qty` | INT64 | Meaning not documented in the repo. |
| `remain_amt` | FLOAT64 | Meaning not documented in the repo. |
| `remain_qty` | INT64 | Meaning not documented in the repo. |
| `start_date` | DATE | Meaning not documented in the repo. |
| `end_date` | DATE | Meaning not documented in the repo. |
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

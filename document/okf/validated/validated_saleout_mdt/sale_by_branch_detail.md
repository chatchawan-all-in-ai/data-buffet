---
type: BigQuery Table
title: "sale_by_branch_detail"
description: "One row = one cleaned copy of the source table `sale_by_branch_detail`, unique on (branch, article_id, distribution_channel, end_date)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=sale_by_branch_detail&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: sale_by_branch_detail
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_incremental", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/BT/sale_by_branch_detail.sqlx"
    title: "Dataform definition (validated/saleout_mdt/BT/sale_by_branch_detail.sqlx)"
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

Validated copy of SALEOUT_MDT `sale_by_branch_detail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `branch`, `article_id`, `distribution_channel`, `end_date`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `branch` | STRING | Meaning not documented in the repo. |
| `article_id` | STRING | Meaning not documented in the repo. |
| `distribution_channel` | STRING | Meaning not documented in the repo. |
| `start_date` | DATE | Meaning not documented in the repo. |
| `end_date` | DATE | Meaning not documented in the repo. |
| `net_inc_tax_mtd` | FLOAT64 | Meaning not documented in the repo. |
| `sale_qty_mtd` | INT64 | Meaning not documented in the repo. |
| `sale_sqm_mtd` | FLOAT64 | Meaning not documented in the repo. |
| `article_name_th` | STRING | Meaning not documented in the repo. |
| `brand` | STRING | Meaning not documented in the repo. |
| `flag_project` | STRING | Meaning not documented in the repo. |
| `item_flag` | STRING | Meaning not documented in the repo. |
| `mch3` | STRING | Meaning not documented in the repo. |
| `mch2` | STRING | Meaning not documented in the repo. |
| `year_date_id` | INT64 | Meaning not documented in the repo. |
| `month_date_id` | STRING | Meaning not documented in the repo. |
| `vendor_id` | STRING | Meaning not documented in the repo. |
| `vendor_name` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/sale_by_branch_detail.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`, `saleout_daily`).
- Reads: [raw_saleout_mdt.sale_by_branch_detail](/initial/raw_saleout_mdt/sale_by_branch_detail.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `branch`, `article_id`, `end_date`.
- Approximate size (BigQuery metadata, 2026-10-31): 14,493 rows, 4.2 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.sale_by_branch_detail`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT branch, article_id, distribution_channel, end_date, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.sale_by_branch_detail`
GROUP BY branch, article_id, distribution_channel, end_date
HAVING n > 1
```

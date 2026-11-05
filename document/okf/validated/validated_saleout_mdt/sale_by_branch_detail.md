---
type: BigQuery Table
title: "sale_by_branch_detail"
description: "One row = one article, branch and sales channel for one report date from source table `sale_by_branch_detail`, unique on (branch, article_id, distribution_channel, end_date)."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of SALEOUT_MDT `sale_by_branch_detail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. `distribution_channel` `Website` is mapped to `Web`. Table meaning: Boonthavorn (BT) sell-out file with month-to-date (MTD) sales of the company products per branch, article and channel; curated derives daily sales from the change in MTD values.

Read by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `branch`, `article_id`, `distribution_channel`, `end_date`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `branch` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `article_id` | STRING | Boonthavorn article (product) code. |
| `distribution_channel` | STRING | Sales channel at Boonthavorn (`Showroom`, `Anyhome`, `Web`). |
| `start_date` | DATE | First day of the reporting period. |
| `end_date` | DATE | Last day covered by the report (figures are counted up to this date). |
| `net_inc_tax_mtd` | FLOAT64 | Month-to-date net sales amount including VAT (THB), cumulative from `start_date` to `end_date`. |
| `sale_qty_mtd` | INT64 | Month-to-date sales quantity, cumulative from `start_date` to `end_date`. |
| `sale_sqm_mtd` | FLOAT64 | Month-to-date sales in square metres, cumulative from `start_date` to `end_date`. |
| `article_name_th` | STRING | Product name in Thai. |
| `brand` | STRING | Product brand. |
| `flag_project` | STRING | Project-sale flag (`Y`/`N`; daily file sends `Project`/`Non-Project`). |
| `item_flag` | STRING | Item movement flag (`REGULAR`, `FAST`, `DISCON` = discontinued). |
| `mch3` | STRING | Boonthavorn merchandise category, top level (department). |
| `mch2` | STRING | Boonthavorn merchandise category, second level. |
| `year_date_id` | INT64 | Year of the report period. |
| `month_date_id` | STRING | Month name of the report period in English (e.g. `July`). |
| `vendor_id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `vendor_name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/sale_by_branch_detail.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`, `saleout_daily`).
- Reads: [raw_saleout_mdt.sale_by_branch_detail](/initial/raw_saleout_mdt/sale_by_branch_detail.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `branch`, `article_id`, `end_date`.

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

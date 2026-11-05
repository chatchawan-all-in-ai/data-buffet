---
type: BigQuery Table
title: "sale_by_branch_mch3"
description: "One row = one branch and merchandise category for one report date from source table `sale_by_branch_mch3`, unique on (vendor_id, branch, mch3)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=sale_by_branch_mch3&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: sale_by_branch_mch3
tags: ["validated", "validated_saleout_mdt", "saleout", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/BT/sale_by_branch_mch3.sqlx"
    title: "Dataform definition (validated/saleout_mdt/BT/sale_by_branch_mch3.sqlx)"
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

Validated copy of SALEOUT_MDT `sale_by_branch_mch3`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Boonthavorn (BT) sales summary of the company products per branch and category: month-to-date and year-to-date sales against last year.
No other repo object reads it.

# Grain and key

One row per `vendor_id`, `branch`, `mch3`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `vendor_id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `vendor_name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `mch3` | STRING | Boonthavorn merchandise category, top level (department). |
| `branch` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `mtd_last_year` | FLOAT64 | Month-to-date sales amount for the same period last year (THB). |
| `mtd_current_year` | FLOAT64 | Month-to-date sales amount this year (THB). |
| `mtd_pct_growth` | FLOAT64 | Month-to-date sales growth versus last year, in percent. |
| `ytd_last_year` | FLOAT64 | Year-to-date sales amount for the same period last year (THB). |
| `ytd_current_year` | FLOAT64 | Year-to-date sales amount this year (THB). |
| `ytd_pct_growth` | FLOAT64 | Year-to-date sales growth versus last year, in percent. |
| `start_date` | DATE | First day of the reporting period. |
| `end_date` | DATE | Last day covered by the report (figures are counted up to this date). |
| `ASATDATE` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/sale_by_branch_mch3.sqlx` (`type: "incremental"`, tags `validated`, `saleout_daily`).
- Reads: [raw_saleout_mdt.sale_by_branch_mch3](/initial/raw_saleout_mdt/sale_by_branch_mch3.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `vendor_id`, `branch`, `mch3`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.sale_by_branch_mch3`
LIMIT 100
```

Duplicate keys:

```sql
SELECT vendor_id, branch, mch3, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.sale_by_branch_mch3`
GROUP BY vendor_id, branch, mch3
HAVING n > 1
```

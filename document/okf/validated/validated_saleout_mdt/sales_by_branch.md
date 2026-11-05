---
type: BigQuery Table
title: "sales_by_branch"
description: "One row = one Boonthavorn branch for one report date from source table `sales_by_branch`, unique on (vendor_id, branch)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=sales_by_branch&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: sales_by_branch
tags: ["validated", "validated_saleout_mdt", "saleout"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/BT/sales_by_branch.sqlx"
    title: "Dataform definition (validated/saleout_mdt/BT/sales_by_branch.sqlx)"
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

Validated copy of SALEOUT_MDT `sales_by_branch`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Boonthavorn (BT) sales summary of the company products per branch: month-to-date and year-to-date amount, quantity and square metres against last year.
No other table or view in this repository reads it.

# Grain and key

One row per `vendor_id`, `branch`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `vendor_id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `vendor_name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `branch` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `mtd_last_year` | FLOAT64 | Month-to-date sales amount for the same period last year (THB). |
| `mtd_current_year` | FLOAT64 | Month-to-date sales amount this year (THB). |
| `mtd_growth` | STRING | Month-to-date sales growth versus last year, as percentage text (e.g. `-4.8%`). |
| `ytd_last_year` | FLOAT64 | Year-to-date sales amount for the same period last year (THB). |
| `ytd_current_year` | FLOAT64 | Year-to-date sales amount this year (THB). |
| `ytd_growth` | STRING | Year-to-date sales growth versus last year, as percentage text (e.g. `67.51%`). |
| `mtd_last_year_qty` | FLOAT64 | Month-to-date sales quantity for the same period last year. |
| `mtd_curr_year_qty` | FLOAT64 | Month-to-date sales quantity this year. |
| `mtd_pct_growth_qty` | FLOAT64 | Month-to-date sales quantity growth versus last year, in percent. |
| `ytd_last_year_qty` | FLOAT64 | Year-to-date sales quantity for the same period last year. |
| `ytd_curr_year_qty` | FLOAT64 | Year-to-date sales quantity this year. |
| `ytd_pct_growth_qty` | FLOAT64 | Year-to-date sales quantity growth versus last year, in percent. |
| `mtd_last_year_sqm` | FLOAT64 | Month-to-date sales in square metres for the same period last year. |
| `mtd_curr_year_sqm` | FLOAT64 | Month-to-date sales in square metres this year. |
| `mtd_pct_growth_sqm` | FLOAT64 | Month-to-date square-metre sales growth versus last year, in percent. |
| `ytd_last_year_sqm` | FLOAT64 | Year-to-date sales in square metres for the same period last year. |
| `ytd_curr_year_sqm` | FLOAT64 | Year-to-date sales in square metres this year. |
| `ytd_pct_growth_sqm` | FLOAT64 | Year-to-date square-metre sales growth versus last year, in percent. |
| `start_date` | DATE | First day of the reporting period. |
| `end_date` | DATE | Last day covered by the report (figures are counted up to this date). |
| `ASATDATE` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/sales_by_branch.sqlx` (`type: "incremental"`, tags `validated`).
- Reads: [raw_saleout_mdt.sales_by_branch](/initial/raw_saleout_mdt/sales_by_branch.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `vendor_id`, `branch`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.sales_by_branch`
LIMIT 100
```

Duplicate keys:

```sql
SELECT vendor_id, branch, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.sales_by_branch`
GROUP BY vendor_id, branch
HAVING n > 1
```

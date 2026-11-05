---
type: BigQuery Table
title: "turnover"
description: "One row = one branch and merchandise category on one snapshot date from source table `turnover`, unique on (vendor_id, branch, mch3)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=turnover&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: turnover
tags: ["validated", "validated_saleout_mdt", "saleout"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/BT/turnover.sqlx"
    title: "Dataform definition (validated/saleout_mdt/BT/turnover.sqlx)"
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

Validated copy of SALEOUT_MDT `turnover`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Stock turnover report from Boonthavorn (BT): stock value at cost, turnover and dead-stock share of the company products per branch and category.
No other repo object reads it.

# Grain and key

One row per `vendor_id`, `branch`, `mch3`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `vendor_id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `vendor_name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `branch` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `mch3` | STRING | Boonthavorn merchandise category, top level (department). |
| `ur_cost_amt` | FLOAT64 | Value of the unrestricted stock at cost for the branch and category. |
| `t_o` | FLOAT64 | Stock turnover (T/O) of the branch and category, in days. |
| `ur_cost_amt_dead` | FLOAT64 | Value at cost of the dead stock for the branch and category. |
| `dead` | STRING | Dead stock share of the stock value, as percentage text (e.g. `35.9%`). |
| `t_o_vendor` | FLOAT64 | Stock turnover (T/O) of the vendor across all branches, in days. |
| `start_date` | DATE | Stock snapshot date (same as `end_date`). |
| `end_date` | DATE | Stock snapshot date. |
| `ASATDATE` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/turnover.sqlx` (`type: "incremental"`, tags `validated`).
- Reads: [raw_saleout_mdt.turnover](/initial/raw_saleout_mdt/turnover.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `vendor_id`, `branch`, `mch3`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.turnover`
LIMIT 100
```

Duplicate keys:

```sql
SELECT vendor_id, branch, mch3, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.turnover`
GROUP BY vendor_id, branch, mch3
HAVING n > 1
```

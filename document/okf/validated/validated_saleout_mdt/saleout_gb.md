---
type: BigQuery Table
title: "saleout_gb"
description: "One row = one cleaned copy of the source table `saleout_gb`, unique on (sale_no, sale_date, branch_code, product_code)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=saleout_gb&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: saleout_gb
tags: ["validated", "validated_saleout_mdt", "saleout", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/GB/saleout_gb.sqlx"
    title: "Dataform definition (validated/saleout_mdt/GB/saleout_gb.sqlx)"
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

Validated copy of SALEOUT_MDT `saleout_gb`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `sale_no`, `sale_date`, `branch_code`, `product_code`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `row_no` | STRING | Meaning not documented in the repo. |
| `sale_no` | STRING | Meaning not documented in the repo. |
| `sale_date` | DATE | Meaning not documented in the repo. |
| `branch_code` | STRING | Meaning not documented in the repo. |
| `branch_name` | STRING | Meaning not documented in the repo. |
| `branch_short_name` | STRING | Meaning not documented in the repo. |
| `product_code` | STRING | Meaning not documented in the repo. |
| `product_name` | STRING | Meaning not documented in the repo. |
| `sale_quantity` | INT64 | Meaning not documented in the repo. |
| `sale_amount` | FLOAT64 | Meaning not documented in the repo. |
| `type` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `reference_no` | STRING | Meaning not documented in the repo. |
| `deposit_no` | STRING | Meaning not documented in the repo. |
| `ASATDATE` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/GB/saleout_gb.sqlx` (`type: "incremental"`, tags `validated`, `saleout_daily`).
- Reads: [raw_saleout_mdt.saleout_gb](/initial/raw_saleout_mdt/saleout_gb.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_date`, `branch_code`, `product_code`, `sale_no`.
- Approximate size (BigQuery metadata, 2026-10-31): 39,484 rows, 10.1 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_gb`
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_no, sale_date, branch_code, product_code, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_gb`
GROUP BY sale_no, sale_date, branch_code, product_code
HAVING n > 1
```

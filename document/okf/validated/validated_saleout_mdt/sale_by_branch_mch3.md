---
type: BigQuery Table
title: "sale_by_branch_mch3"
description: "One row = one cleaned copy of the source table `sale_by_branch_mch3`, unique on (vendor_id, branch, mch3)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=sale_by_branch_mch3&page=table"
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of SALEOUT_MDT `sale_by_branch_mch3`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `vendor_id`, `branch`, `mch3`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `vendor_id` | STRING | Meaning not documented in the repo. |
| `vendor_name` | STRING | Meaning not documented in the repo. |
| `mch3` | STRING | Meaning not documented in the repo. |
| `branch` | STRING | Meaning not documented in the repo. |
| `mtd_last_year` | FLOAT64 | Meaning not documented in the repo. |
| `mtd_current_year` | FLOAT64 | Meaning not documented in the repo. |
| `mtd_pct_growth` | FLOAT64 | Meaning not documented in the repo. |
| `ytd_last_year` | FLOAT64 | Meaning not documented in the repo. |
| `ytd_current_year` | FLOAT64 | Meaning not documented in the repo. |
| `ytd_pct_growth` | FLOAT64 | Meaning not documented in the repo. |
| `start_date` | DATE | Meaning not documented in the repo. |
| `end_date` | DATE | Meaning not documented in the repo. |
| `ASATDATE` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/sale_by_branch_mch3.sqlx` (`type: "incremental"`, tags `validated`, `saleout_daily`).
- Reads: [raw_saleout_mdt.sale_by_branch_mch3](/initial/raw_saleout_mdt/sale_by_branch_mch3.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `vendor_id`, `branch`, `mch3`.
- Approximate size (BigQuery metadata, 2026-10-31): 19 rows, 3.5 KB.

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

---
type: BigQuery Table
title: "saleout_dh"
description: "One row = one cleaned copy of the source table `saleout_dh`, unique on (sale_date, branch_code, product_code, is_return)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=saleout_dh&page=table"
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_full", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/DH/saleout_dh.sqlx"
    title: "Dataform definition (validated/saleout_mdt/DH/saleout_dh.sqlx)"
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

Validated copy of SALEOUT_MDT `saleout_dh`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `sale_date`, `branch_code`, `product_code`, `is_return`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Meaning not documented in the repo. |
| `store_code` | STRING | Meaning not documented in the repo. |
| `branch_code` | STRING | Meaning not documented in the repo. |
| `product_code` | STRING | Meaning not documented in the repo. |
| `product_name` | STRING | Meaning not documented in the repo. |
| `sale_qty` | INT64 | Meaning not documented in the repo. |
| `sale_amount` | FLOAT64 | Meaning not documented in the repo. |
| `is_return` | BOOL | Meaning not documented in the repo. |
| `source_folder` | STRING | Meaning not documented in the repo. |
| `file_modified` | TIMESTAMP | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/DH/saleout_dh.sqlx` (`type: "table"`, tags `validated`, `validated_full`, `saleout_daily`).
- Reads: [raw_saleout_mdt.saleout_dh](/initial/raw_saleout_mdt/saleout_dh.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `asatdate`, cluster by `branch_code`, `product_code`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,839 rows, 435.9 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_dh`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_date, branch_code, product_code, is_return, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_dh`
GROUP BY sale_date, branch_code, product_code, is_return
HAVING n > 1
```

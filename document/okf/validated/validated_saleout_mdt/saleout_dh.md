---
type: BigQuery Table
title: "saleout_dh"
description: "One row = one product, branch, sale date and sale/return flag from source table `saleout_dh`, unique on (sale_date, branch_code, product_code, is_return)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=saleout_dh&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: saleout_dh
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

Daily sell-out of the company products at DoHome branches, from monthly SharePoint files in SALEOUT_MDT `saleout_dh`. Rows are filtered out only when raw `SALES_DATE`, `BRANCH_CODE` or `PRODUCT_CODE` is NULL; blank codes survive this filter and become NULL through `cleanCode`. Sale and extract dates are parsed, and codes, product names and source folders are cleaned with the shared helpers. Rows with the latest `file_modified` per source folder and sale month are kept, including ties. Quantity and amount are summed by `sale_date`, `branch_code`, `product_code` and `is_return`; quantity is rounded and cast to INT64, and `asatdate` is the maximum extract date in each group.
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `sale_date`, `branch_code`, `product_code`, `is_return`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Sale date. |
| `store_code` | STRING | Retail chain code, always `DH` (DoHome). |
| `branch_code` | STRING | Cleaned DoHome branch code (`M...` = DoHome To Go branches); blank codes become NULL. |
| `product_code` | STRING | Cleaned DoHome product code (not a barcode); blank codes become NULL. |
| `product_name` | STRING | Any product name from the rows in the group (`ANY_VALUE`). |
| `sale_qty` | INT64 | SUM of source `SALES_QTY` per sale date, branch, product and return flag, rounded and cast to INT64. |
| `sale_amount` | FLOAT64 | SUM of source `SALES_AMOUNT` per sale date, branch, product and return flag (THB; negative = return). |
| `is_return` | BOOL | TRUE for return rows (negative amount); sales and returns are kept on separate rows. |
| `source_folder` | STRING | Any source SharePoint folder (DoHome sales zone) from the rows in the group (`ANY_VALUE`). |
| `file_modified` | TIMESTAMP | Maximum source-file last-modified timestamp in the group, after keeping the latest timestamp per folder and sale month (including ties); unparseable or NULL source timestamps become `1900-01-01`. |
| `asatdate` | DATE | MAX of the extract dates (raw `ASATDATE` parsed to DATE) in the group; the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/DH/saleout_dh.sqlx` (`type: "table"`, tags `validated`, `validated_full`, `saleout_daily`).
- Reads: [raw_saleout_mdt.saleout_dh](/initial/raw_saleout_mdt/saleout_dh.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `asatdate`, cluster by `branch_code`, `product_code`.

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

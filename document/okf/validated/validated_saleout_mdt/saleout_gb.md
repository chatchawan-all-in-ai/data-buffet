---
type: BigQuery Table
title: "saleout_gb"
description: "One row = one product line of one Global House bill from source table `saleout_gb`, unique on (sale_no, sale_date, branch_code, product_code)."
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
generated: { by: "agent:codex", at: "2026-11-09T02:15:58+00:00" }
status: draft
---

# What it is

Validated copy of SALEOUT_MDT `saleout_gb`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. Rows with an empty `Sale_Date` are dropped; the sale date is parsed from both file formats (MM/DD/YYYY and DD/MM/YYYY, Gregorian or Buddhist year) and the `type` values `ขาย`/`รับคืน` are mapped to `SALE`/`RETURN`. Table meaning: Daily sell-out bill lines of the company products at Global House branches, including returns.

Read by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `sale_no`, `sale_date`, `branch_code`, `product_code`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `row_no` | STRING | Line number of the row in the report file. |
| `sale_no` | STRING | Global House bill (sales document) number. |
| `sale_date` | DATE | Sale (bill) date. If the year is at least 2500, it is parsed as Buddhist-era DD/MM/YYYY with 543 subtracted from the year; otherwise, DD/MM/YYYY is used when raw `ASATDATE >= '20261015'`, and MM/DD/YYYY is used before that cutoff. Unparseable dates become NULL. |
| `branch_code` | STRING | Global House branch code (e.g. `GH-218`). |
| `branch_name` | STRING | Global House branch name. |
| `branch_short_name` | STRING | Short branch abbreviation used in bill numbers. |
| `product_code` | STRING | Global House product code (13-digit barcode). |
| `product_name` | STRING | Product name. |
| `sale_quantity` | INT64 | Sales quantity (negative = return). |
| `sale_amount` | FLOAT64 | Sales amount (THB; negative = return). Commas and apostrophes are removed before casting to FLOAT64. |
| `type` | STRING | Document type: `SALE` or `RETURN` (newer files send Thai `ขาย`/`รับคืน`). |
| `reference_no` | STRING | Original bill number referenced by a return. |
| `deposit_no` | STRING | Deposit document number linked to the bill. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/GB/saleout_gb.sqlx` (`type: "incremental"`, tags `validated`, `saleout_daily`).
- Reads: [raw_saleout_mdt.saleout_gb](/initial/raw_saleout_mdt/saleout_gb.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_date`, `branch_code`, `product_code`, `sale_no`.

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

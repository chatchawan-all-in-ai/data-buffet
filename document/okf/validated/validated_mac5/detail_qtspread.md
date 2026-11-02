---
type: BigQuery Table
title: "detail_qtspread"
description: "One row = one item line of a quotation spread (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=detail_qtspread&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: detail_qtspread
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/detail_qtspread.sqlx"
    title: "Dataform definition (validated/mac5/detail_qtspread.sqlx)"
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

Validated copy of MAC5 `detail_qtspread`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Item lines of quotation spreads: stock code and quantity taken from a quotation detail line into one order.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Row identifier of the spread line. |
| `ref_id` | INT64 | Quotation spread identifier (`main_qtspread.id`). |
| `qtid` | INT64 | Quotation identifier (`tbook_quotation.id`). |
| `quodeid` | STRING | Quotation detail line identifier (`tbook_quodetail.id`). |
| `stkcode` | STRING | MAC5 stock code of the item. |
| `quantity` | FLOAT64 | Quantity of the item spread into this order. |
| `price` | FLOAT64 | Unit price of the item. |
| `total` | STRING | Line total of the item. |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dinsert` | DATETIME | Date and time the row was created. |
| `dupdate` | DATETIME | Date and time the row was last updated. |
| `status` | STRING | Status code of the spread line (1 = active, 3 = cancelled). |
| `link` | STRING | Link reference of the spread line. |
| `type` | STRING | Line type of the spread line. |
| `fandex` | STRING | FANDEX reference of the spread line. |
| `itemsize` | STRING | Item size of the spread line. |

# How it is built

- Definition: `definitions/validated/mac5/detail_qtspread.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.detail_qtspread](/initial/raw_mac5_ag01/detail_qtspread.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY dupdate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 725,492 rows, 62.1 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.detail_qtspread`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.detail_qtspread`
GROUP BY company_id, id
HAVING n > 1
```

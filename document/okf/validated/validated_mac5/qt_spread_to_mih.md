---
type: BigQuery Table
title: "qt_spread_to_mih"
description: "One row = one link from a quotation spread to a pre-order (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=qt_spread_to_mih&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: qt_spread_to_mih
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/qt_spread_to_mih.sqlx"
    title: "Dataform definition (validated/mac5/qt_spread_to_mih.sqlx)"
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

Validated copy of MAC5 `qt_spread_to_mih`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Links from quotation spreads (main_qtspread) to the pre-order numbers created from them.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Row identifier of the link. |
| `qt_spread_ref_id` | INT64 | Quotation spread identifier (`main_qtspread.id`). |
| `qtid` | STRING | Quotation identifier (`tbook_quotation.id`). |
| `mihvnos` | STRING | Document number, unique within company and document type. |
| `status` | INT64 | Status flag of the link (1 = active). |
| `rdysendtomac5` | INT64 | Ready-to-send-to-MAC5 flag. |
| `sto` | STRING | Stock location code of the order. |

# How it is built

- Definition: `definitions/validated/mac5/qt_spread_to_mih.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.qt_spread_to_mih](/initial/raw_mac5_ag01/qt_spread_to_mih.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY mihvnos desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 543,576 rows, 30.5 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.qt_spread_to_mih`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.qt_spread_to_mih`
GROUP BY company_id, id
HAVING n > 1
```

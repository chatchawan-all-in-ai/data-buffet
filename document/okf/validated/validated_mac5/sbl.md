---
type: BigQuery Table
title: "sbl"
description: "One row = one stock balance for one item in one warehouse (per company), unique on (company_id, sblstk, sblsto)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=sbl&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: sbl
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/sbl.sqlx"
    title: "Dataform definition (validated/mac5/sbl.sqlx)"
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

Validated copy of MAC5 `sbl`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Stock balances per item and warehouse.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `sblstk`, `sblsto`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `sblstk` | STRING | Stock code of the balance row. |
| `sblsto` | STRING | Warehouse code of the balance row (joins `sto.stocode`). |
| `sblquan` | FLOAT64 | Stock balance quantity in the base unit. |
| `sblquanp2` | FLOAT64 | Stock balance quantity in the second unit. |

# How it is built

- Definition: `definitions/validated/mac5/sbl.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.sbl](/initial/raw_mac5_ag01/sbl.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: not partitioned; cluster by `company_id`, `sblstk`, `sblsto`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.sbl`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, sblstk, sblsto, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.sbl`
GROUP BY company_id, sblstk, sblsto
HAVING n > 1
```

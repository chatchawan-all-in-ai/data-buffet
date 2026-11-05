---
type: BigQuery Table
title: "comboset"
description: "One row = one item in a combo set (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=comboset&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: comboset
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/comboset.sqlx"
    title: "Dataform definition (validated/mac5/comboset.sqlx)"
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

Validated copy of MAC5 `comboset`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Items that make up each combo set, with quantity and list price.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Running ID of the combo set line row. |
| `combostk` | STRING | Combo set code the line belongs to (joins `combostk.combostk`). |
| `stkcode` | STRING | Stock code of the item in the combo set. |
| `date` | DATETIME | Date and time the row was created. |
| `uinsert` | STRING | User code of the person who created the record. |
| `uupdate` | STRING | User code of the person who last updated the record. |
| `status` | INT64 | Status code of the combo set line (1 = active). |
| `quantity` | INT64 | Quantity of the item in the combo set. |
| `price` | FLOAT64 | Price of the item in the combo set. |
| `lp` | FLOAT64 | List price of the item. |

# How it is built

- Definition: `definitions/validated/mac5/comboset.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.comboset](/initial/raw_mac5_ag01/comboset.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY date desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.comboset`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.comboset`
GROUP BY company_id, id
HAVING n > 1
```

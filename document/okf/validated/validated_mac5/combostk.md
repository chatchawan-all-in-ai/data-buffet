---
type: BigQuery Table
title: "combostk"
description: "One row = one combo set (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=combostk&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: combostk
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/combostk.sqlx"
    title: "Dataform definition (validated/mac5/combostk.sqlx)"
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

Validated copy of MAC5 `combostk`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Combo set headers: combo set code, status and audit fields.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Running ID of the combo set header row. |
| `combostk` | STRING | Combo set code (e.g. `COMBOSET56`). |
| `date` | DATETIME | Date and time the row was created. |
| `uinsert` | STRING | User code of the person who created the record. |
| `uupdate` | STRING | User code of the person who last updated the record. |
| `status` | INT64 | Status code of the combo set (1, 2). |
| `notecomboset` | STRING | Note on the combo set. |

# How it is built

- Definition: `definitions/validated/mac5/combostk.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.combostk](/initial/raw_mac5_ag01/combostk.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY date desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.combostk`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.combostk`
GROUP BY company_id, id
HAVING n > 1
```

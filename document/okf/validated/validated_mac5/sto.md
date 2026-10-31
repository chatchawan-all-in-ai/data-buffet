---
type: BigQuery Table
title: "sto"
description: "One row = one reference code table (sto), unique on (company_id, stocode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=sto&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: sto
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/sto.sqlx"
    title: "Dataform definition (validated/mac5/sto.sqlx)"
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

Validated copy of MAC5 `sto`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: reference code table (sto). Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_store](/dimension/dim_store.md).

# Grain and key

One row per `company_id`, `stocode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `stocode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `stogroup` | STRING | Meaning not documented in the repo. |
| `stodesct` | STRING | Meaning not documented in the repo. |
| `stodesce` | STRING | Meaning not documented in the repo. |
| `stolock` | INT64 | Meaning not documented in the repo. |
| `stohide` | INT64 | Meaning not documented in the repo. |
| `stoeditdt` | DATETIME | Meaning not documented in the repo. |
| `stoeditmf` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/sto.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.sto](/initial/raw_mac5_ag01/sto.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stoeditdt desc, stodesct desc, stodesce desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `stocode`.
- Approximate size (BigQuery metadata, 2026-10-31): 601 rows, 76.8 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.sto`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stocode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.sto`
GROUP BY company_id, stocode
HAVING n > 1
```

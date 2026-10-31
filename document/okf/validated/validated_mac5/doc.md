---
type: BigQuery Table
title: "doc"
description: "One row = one document type reference, unique on (company_id, doccode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=doc&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: doc
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/doc.sqlx"
    title: "Dataform definition (validated/mac5/doc.sqlx)"
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

Validated copy of MAC5 `doc`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: document type reference. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `doccode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `doccode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `docgroup` | STRING | Meaning not documented in the repo. |
| `docdesct` | STRING | Meaning not documented in the repo. |
| `docdesce` | STRING | Meaning not documented in the repo. |
| `doclock` | INT64 | Meaning not documented in the repo. |
| `docacc` | STRING | Meaning not documented in the repo. |
| `docdebit` | INT64 | Meaning not documented in the repo. |
| `docrefwe` | STRING | Meaning not documented in the repo. |
| `dochide` | INT64 | Meaning not documented in the repo. |
| `doceditdt` | DATETIME | Meaning not documented in the repo. |
| `doceditmf` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/doc.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.doc](/initial/raw_mac5_ag01/doc.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY doceditdt desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `doccode`.
- Approximate size (BigQuery metadata, 2026-10-31): 26 rows, 3.0 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.doc`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, doccode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.doc`
GROUP BY company_id, doccode
HAVING n > 1
```

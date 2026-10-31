---
type: BigQuery Table
title: "tbook_givestk"
description: "One row = one booking: stock given, unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_givestk&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_givestk.sqlx"
    title: "Dataform definition (validated/mac5/tbook_givestk.sqlx)"
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

Validated copy of MAC5 `tbook_givestk`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: booking: stock given. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Surrogate identifier from the source system (the primary key). |
| `qtid` | INT64 | Meaning not documented in the repo. |
| `qtspread_ref_id` | INT64 | Meaning not documented in the repo. |
| `quodeid` | INT64 | Meaning not documented in the repo. |
| `quolinkdel` | INT64 | Meaning not documented in the repo. |
| `stkcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `stkgive` | STRING | Meaning not documented in the repo. |
| `quantity` | INT64 | Meaning not documented in the repo. |
| `datetimekey` | DATETIME | Meaning not documented in the repo. |
| `status` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |

# How it is built

- Definition: `definitions/validated/mac5/tbook_givestk.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_givestk](/initial/raw_mac5_ag01/tbook_givestk.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY datetimekey desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 203,200 rows, 19.0 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_givestk`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbook_givestk`
GROUP BY company_id, id
HAVING n > 1
```

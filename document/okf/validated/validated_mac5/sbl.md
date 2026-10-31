---
type: BigQuery Table
title: "sbl"
description: "One row = one reference code table (sbl), unique on (company_id, sblstk, sblsto)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=sbl&page=table"
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

Validated copy of MAC5 `sbl`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: reference code table (sbl). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `sblstk`, `sblsto`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `sblstk` | STRING | Likely stock (SKU) code (inferred from the column name only; not documented in the repo). |
| `sblsto` | STRING | Meaning not documented in the repo. |
| `sblquan` | FLOAT64 | Meaning not documented in the repo. |
| `sblquanp2` | FLOAT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/sbl.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.sbl](/initial/raw_mac5_ag01/sbl.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `sblstk`, `sblsto`.
- Approximate size (BigQuery metadata, 2026-10-31): 116,487 rows, 4.7 MB.

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

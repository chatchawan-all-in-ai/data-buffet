---
type: BigQuery Table
title: "stk_mkt"
description: "One row = one stock marketing attributes, unique on (company_id, stkcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stk_mkt&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stk_mkt.sqlx"
    title: "Dataform definition (validated/mac5/stk_mkt.sqlx)"
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

Validated copy of MAC5 `stk_mkt`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: stock marketing attributes. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `stkcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `stkcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `stkgroup` | STRING | Meaning not documented in the repo. |
| `stkdesct1` | STRING | Meaning not documented in the repo. |
| `zgroup1` | STRING | Meaning not documented in the repo. |
| `zgroup2` | STRING | Meaning not documented in the repo. |
| `zsize` | STRING | Meaning not documented in the repo. |
| `zcolor` | STRING | Meaning not documented in the repo. |
| `zgroup3` | STRING | Meaning not documented in the repo. |
| `zgroup4` | STRING | Meaning not documented in the repo. |
| `zgroup5` | STRING | Meaning not documented in the repo. |
| `zgroup6` | STRING | Meaning not documented in the repo. |
| `zgroup7` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/stk_mkt.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.stk_mkt](/initial/raw_mac5_ag01/stk_mkt.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stkdesct1 DESC) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `stkcode`.
- Approximate size (BigQuery metadata, 2026-10-31): 77,272 rows, 9.8 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stk_mkt`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stkcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stk_mkt`
GROUP BY company_id, stkcode
HAVING n > 1
```

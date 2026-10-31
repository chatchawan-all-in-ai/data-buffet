---
type: BigQuery Table
title: "ttrip"
description: "One row = one delivery trip, unique on (company_id, frun, fcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=ttrip&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/ttrip.sqlx"
    title: "Dataform definition (validated/mac5/ttrip.sqlx)"
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

Validated copy of MAC5 `ttrip`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: delivery trip. Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_delivery](/dimension/dim_delivery.md), [fact_table.fact_delivery](/fact/fact_delivery.md).

# Grain and key

One row per `company_id`, `frun`, `fcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `frun` | STRING | Meaning not documented in the repo. |
| `fmaster` | STRING | Meaning not documented in the repo. |
| `fcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `fdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `fvehicle` | STRING | Meaning not documented in the repo. |
| `fother` | STRING | Meaning not documented in the repo. |
| `fprice` | INT64 | Likely price (inferred from the column name only; not documented in the repo). |
| `fbuddy` | INT64 | Meaning not documented in the repo. |
| `fdeduct_detail` | STRING | Meaning not documented in the repo. |
| `fdeduct_monkey` | FLOAT64 | Meaning not documented in the repo. |
| `fdeduct_money` | FLOAT64 | Meaning not documented in the repo. |
| `ftype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `fcomplete` | STRING | Meaning not documented in the repo. |
| `foil` | STRING | Meaning not documented in the repo. |
| `fpass_date` | STRING | Meaning not documented in the repo. |
| `fpay` | STRING | Meaning not documented in the repo. |
| `foil_deduct` | INT64 | Meaning not documented in the repo. |
| `loadip` | INT64 | Meaning not documented in the repo. |
| `loadvnos` | STRING | Meaning not documented in the repo. |
| `fremark` | STRING | Likely free-text remark (inferred from the column name only; not documented in the repo). |
| `flitre_price` | FLOAT64 | Meaning not documented in the repo. |
| `flitre` | FLOAT64 | Meaning not documented in the repo. |
| `fcubic` | FLOAT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/ttrip.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.ttrip](/initial/raw_mac5_ag01/ttrip.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY fdate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `frun`, `fcode`.
- Approximate size (BigQuery metadata, 2026-10-31): 293,139 rows, 42.6 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.ttrip`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, frun, fcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.ttrip`
GROUP BY company_id, frun, fcode
HAVING n > 1
```

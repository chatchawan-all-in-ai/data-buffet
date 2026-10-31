---
type: BigQuery Table
title: "mkt_per"
description: "One row = one marketing personnel, unique on (company_id, percode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mkt_per&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mkt_per
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mkt_per.sqlx"
    title: "Dataform definition (validated/mac5/mkt_per.sqlx)"
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

Validated copy of MAC5 `mkt_per`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: marketing personnel. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `percode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `percode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `pername` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `perstart` | DATETIME | Meaning not documented in the repo. |
| `perend` | DATETIME | Meaning not documented in the repo. |
| `perzone` | STRING | Meaning not documented in the repo. |
| `persector` | STRING | Meaning not documented in the repo. |
| `zseq` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/mkt_per.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mkt_per](/initial/raw_mac5_ag01/mkt_per.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY perstart desc, perend desc, pername desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `percode`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,695 rows, 188.9 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mkt_per`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, percode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mkt_per`
GROUP BY company_id, percode
HAVING n > 1
```

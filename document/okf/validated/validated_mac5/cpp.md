---
type: BigQuery Table
title: "cpp"
description: "One row = one reference code table (cpp), unique on (company_id, rowguid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cpp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cpp
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cpp.sqlx"
    title: "Dataform definition (validated/mac5/cpp.sqlx)"
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

Validated copy of MAC5 `cpp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: reference code table (cpp). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `rowguid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `rowguid` | STRING | Meaning not documented in the repo. |
| `cppstkid` | STRING | Meaning not documented in the repo. |
| `cpplinkid` | INT64 | Meaning not documented in the repo. |
| `cppvnosid` | STRING | Meaning not documented in the repo. |
| `cppdateid` | DATETIME | Meaning not documented in the repo. |
| `cppcusid` | STRING | Meaning not documented in the repo. |
| `cppjob` | STRING | Meaning not documented in the repo. |
| `cppdep` | STRING | Meaning not documented in the repo. |
| `cppper` | STRING | Meaning not documented in the repo. |
| `cppdoc` | STRING | Meaning not documented in the repo. |
| `cppmec` | STRING | Meaning not documented in the repo. |
| `cppsto` | STRING | Meaning not documented in the repo. |
| `cppstkreq` | FLOAT64 | Meaning not documented in the repo. |
| `cppstkcut1` | FLOAT64 | Meaning not documented in the repo. |
| `cppstkcut2` | FLOAT64 | Meaning not documented in the repo. |
| `cppsumreq` | FLOAT64 | Meaning not documented in the repo. |
| `cppsumcut1` | FLOAT64 | Meaning not documented in the repo. |
| `cppsumcut2` | FLOAT64 | Meaning not documented in the repo. |
| `cppclearstk` | INT64 | Meaning not documented in the repo. |
| `cppclearsum` | INT64 | Meaning not documented in the repo. |
| `cppclearuser` | INT64 | Meaning not documented in the repo. |
| `cppclearall` | INT64 | Meaning not documented in the repo. |
| `cppcurc` | INT64 | Meaning not documented in the repo. |
| `cppexchg` | FLOAT64 | Meaning not documented in the repo. |
| `cppcut` | INT64 | Meaning not documented in the repo. |
| `cppdelvdate` | DATETIME | Meaning not documented in the repo. |
| `cpplistno` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/cpp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.cpp](/initial/raw_mac5_ag01/cpp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY cppdateid desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `rowguid`.
- Approximate size (BigQuery metadata, 2026-10-31): 179,168 rows, 38.6 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cpp`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, rowguid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cpp`
GROUP BY company_id, rowguid
HAVING n > 1
```

---
type: BigQuery Table
title: "userloginanyprogram"
description: "One row = one user login log, unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=userloginanyprogram&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/userloginanyprogram.sqlx"
    title: "Dataform definition (validated/mac5/userloginanyprogram.sqlx)"
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

Validated copy of MAC5 `userloginanyprogram`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: user login log. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Surrogate identifier from the source system (the primary key). |
| `username` | STRING | Meaning not documented in the repo. |
| `password` | STRING | Meaning not documented in the repo. |
| `actionapp` | STRING | Meaning not documented in the repo. |
| `name` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `notes` | STRING | Meaning not documented in the repo. |
| `department` | STRING | Meaning not documented in the repo. |
| `levelaction` | STRING | Meaning not documented in the repo. |
| `email` | STRING | Meaning not documented in the repo. |
| `token` | STRING | Meaning not documented in the repo. |
| `tokenexpiry` | DATETIME | Meaning not documented in the repo. |
| `istokenvalid` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/userloginanyprogram.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.userloginanyprogram](/initial/raw_mac5_ag01/userloginanyprogram.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY username desc, name desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 98 rows, 18.0 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.userloginanyprogram`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.userloginanyprogram`
GROUP BY company_id, id
HAVING n > 1
```

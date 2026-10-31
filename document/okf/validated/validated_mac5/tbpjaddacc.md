---
type: BigQuery Table
title: "tbpjaddacc"
description: "One row = one project additional account, unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbpjaddacc&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbpjaddacc.sqlx"
    title: "Dataform definition (validated/mac5/tbpjaddacc.sqlx)"
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

Validated copy of MAC5 `tbpjaddacc`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: project additional account. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Surrogate identifier from the source system (the primary key). |
| `pjid` | STRING | Meaning not documented in the repo. |
| `accid` | STRING | Meaning not documented in the repo. |
| `accname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `acctype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `acctype2` | STRING | Meaning not documented in the repo. |
| `accpow` | STRING | Meaning not documented in the repo. |
| `conid` | STRING | Meaning not documented in the repo. |
| `conname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `contel` | STRING | Meaning not documented in the repo. |
| `condetail` | STRING | Meaning not documented in the repo. |
| `uinsert` | STRING | Meaning not documented in the repo. |
| `insertdate` | DATE | Meaning not documented in the repo. |
| `textnote` | STRING | Meaning not documented in the repo. |
| `nickname` | STRING | Meaning not documented in the repo. |
| `religion` | STRING | Meaning not documented in the repo. |
| `birthdate` | DATE | Meaning not documented in the repo. |
| `lineidper` | STRING | Meaning not documented in the repo. |
| `emailper` | STRING | Meaning not documented in the repo. |
| `idcardper` | STRING | Meaning not documented in the repo. |
| `addressper` | STRING | Meaning not documented in the repo. |
| `country` | STRING | Meaning not documented in the repo. |
| `province` | STRING | Meaning not documented in the repo. |
| `district` | STRING | Meaning not documented in the repo. |
| `sub_district` | STRING | Meaning not documented in the repo. |
| `zipcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `spousefullname` | STRING | Meaning not documented in the repo. |
| `birthdatespouse` | DATE | Meaning not documented in the repo. |
| `numberofchildren` | STRING | Meaning not documented in the repo. |
| `favoriteactivity` | STRING | Meaning not documented in the repo. |
| `unfavoriteactivity` | STRING | Meaning not documented in the repo. |
| `trait` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/tbpjaddacc.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbpjaddacc](/initial/raw_mac5_ag01/tbpjaddacc.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY insertdate desc, accname desc, conname desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 7,213 rows, 1.9 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbpjaddacc`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbpjaddacc`
GROUP BY company_id, id
HAVING n > 1
```

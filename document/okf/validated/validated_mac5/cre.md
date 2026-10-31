---
type: BigQuery Table
title: "cre"
description: "One row = one reference code table (cre), unique on (company_id, crecode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cre&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cre
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cre.sqlx"
    title: "Dataform definition (validated/mac5/cre.sqlx)"
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

Validated copy of MAC5 `cre`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: reference code table (cre). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `crecode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `crecode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `cregroup` | STRING | Meaning not documented in the repo. |
| `crenamet` | STRING | Meaning not documented in the repo. |
| `crenamee` | STRING | Meaning not documented in the repo. |
| `crecontactt` | STRING | Meaning not documented in the repo. |
| `crecontacte` | STRING | Meaning not documented in the repo. |
| `creadd1at` | STRING | Meaning not documented in the repo. |
| `creadd2at` | STRING | Meaning not documented in the repo. |
| `creadd3at` | STRING | Meaning not documented in the repo. |
| `creadd1ae` | STRING | Meaning not documented in the repo. |
| `creadd2ae` | STRING | Meaning not documented in the repo. |
| `creadd3ae` | STRING | Meaning not documented in the repo. |
| `cretel` | STRING | Meaning not documented in the repo. |
| `cretaxnos` | STRING | Meaning not documented in the repo. |
| `crezone` | STRING | Meaning not documented in the repo. |
| `cregrade` | STRING | Meaning not documented in the repo. |
| `crelimit` | FLOAT64 | Meaning not documented in the repo. |
| `cretaxclass` | FLOAT64 | Meaning not documented in the repo. |
| `cregoodsdef` | INT64 | Meaning not documented in the repo. |
| `crecreditterm` | INT64 | Meaning not documented in the repo. |
| `credate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `crehide` | INT64 | Meaning not documented in the repo. |
| `crefax` | STRING | Meaning not documented in the repo. |
| `creemail` | STRING | Meaning not documented in the repo. |
| `cretarget` | FLOAT64 | Meaning not documented in the repo. |
| `crememo` | STRING | Meaning not documented in the repo. |
| `creac` | STRING | Meaning not documented in the repo. |
| `crelock` | INT64 | Meaning not documented in the repo. |
| `creoname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `creprice` | STRING | Likely price (inferred from the column name only; not documented in the repo). |
| `creeditlk` | DATETIME | Meaning not documented in the repo. |
| `crerefwe` | STRING | Meaning not documented in the repo. |
| `cresortnt` | STRING | Meaning not documented in the repo. |
| `cresortne` | STRING | Meaning not documented in the repo. |
| `crecardid` | STRING | Meaning not documented in the repo. |
| `creeditdt` | DATETIME | Meaning not documented in the repo. |
| `creeditmf` | STRING | Meaning not documented in the repo. |
| `cretaxtype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `creinex` | INT64 | Meaning not documented in the repo. |
| `crebranch` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/cre.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.cre](/initial/raw_mac5_ag01/cre.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY crenamet desc, crenamee desc, credate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `crecode`.
- Approximate size (BigQuery metadata, 2026-10-31): 15,492 rows, 6.3 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cre`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, crecode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cre`
GROUP BY company_id, crecode
HAVING n > 1
```

---
type: BigQuery Table
title: "chq"
description: "One row = one cheque / payment instrument, unique on (company_id, chqno, chqbank, chqdatec, chqtag)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=chq&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/chq.sqlx"
    title: "Dataform definition (validated/mac5/chq.sqlx)"
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

Validated copy of MAC5 `chq` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: cheque / payment instrument. Table meaning is inferred from column prefixes.
Used by: [fact_table.fact_chq](/fact/fact_chq.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row per `company_id`, `chqno`, `chqbank`, `chqdatec`, `chqtag`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `chqno` | STRING | Meaning not documented in the repo. |
| `chqbank` | STRING | Meaning not documented in the repo. |
| `chqacode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `chqcus` | STRING | Likely customer code (inferred from the column name only; not documented in the repo). |
| `chqdatec` | DATETIME | Meaning not documented in the repo. |
| `chqdater` | DATETIME | Meaning not documented in the repo. |
| `chqdatep` | DATETIME | Meaning not documented in the repo. |
| `chqtype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `chqstatus` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |
| `chqtotal` | FLOAT64 | Likely total amount (inferred from the column name only; not documented in the repo). |
| `chqgl` | INT64 | Meaning not documented in the repo. |
| `chqmi` | INT64 | Meaning not documented in the repo. |
| `chqown` | INT64 | Meaning not documented in the repo. |
| `chqtag` | INT64 | Meaning not documented in the repo. |
| `chqstatusn` | INT64 | Meaning not documented in the repo. |
| `chqlock` | INT64 | Meaning not documented in the repo. |
| `chqpassgl` | INT64 | Meaning not documented in the repo. |
| `chqjob` | STRING | Meaning not documented in the repo. |
| `chqdep` | STRING | Meaning not documented in the repo. |
| `chqper` | STRING | Meaning not documented in the repo. |
| `chqzon` | STRING | Meaning not documented in the repo. |
| `chqrcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `chqeditlk` | DATETIME | Meaning not documented in the repo. |
| `chqkeyuser` | STRING | Meaning not documented in the repo. |
| `chqkeydate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `chqdeduct` | FLOAT64 | Meaning not documented in the repo. |
| `chqecode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `chqbranch` | STRING | Meaning not documented in the repo. |
| `chqmec` | STRING | Meaning not documented in the repo. |
| `chqdatev` | DATETIME | Meaning not documented in the repo. |
| `chqmemo_raw` | STRING | Meaning not documented in the repo. |
| `chqmemo` | STRING | Meaning not documented in the repo. |
| `extract_text` | STRING | Meaning not documented in the repo. |
| `extract_value` | ARRAY<STRUCT<extract_date DATE, extract_amount FLOAT64>> | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/chq.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.chq](/initial/raw_mac5_ag01/chq.md), [raw_mac5_aa05.chq](/initial/raw_mac5_aa05/chq.md), [raw_mac5_ab01.chq](/initial/raw_mac5_ab01/chq.md), [raw_mac5_ac02.chq](/initial/raw_mac5_ac02/chq.md), [raw_mac5_ak02.chq](/initial/raw_mac5_ak02/chq.md), `function_dataset.EXTRACT_CHQ_DATA` (UDF).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY chqkeydate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `chqno`.
- Approximate size (BigQuery metadata, 2026-10-31): 160,939 rows, 31.8 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.chq`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, chqno, chqbank, chqdatec, chqtag, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.chq`
GROUP BY company_id, chqno, chqbank, chqdatec, chqtag
HAVING n > 1
```

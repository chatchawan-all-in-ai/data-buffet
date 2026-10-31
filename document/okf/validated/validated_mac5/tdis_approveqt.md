---
type: BigQuery Table
title: "tdis_approveqt"
description: "One row = one quotation approval (distribution), unique on (company_id, docno, stktype)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tdis_approveqt&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tdis_approveqt
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tdis_approveqt.sqlx"
    title: "Dataform definition (validated/mac5/tdis_approveqt.sqlx)"
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

Validated copy of MAC5 `tdis_approveqt`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: quotation approval (distribution). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `docno`, `stktype`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `docno` | STRING | Meaning not documented in the repo. |
| `lv1` | STRING | Meaning not documented in the repo. |
| `lv2` | STRING | Meaning not documented in the repo. |
| `lv3` | STRING | Meaning not documented in the repo. |
| `note1` | STRING | Meaning not documented in the repo. |
| `note2` | STRING | Meaning not documented in the repo. |
| `note3` | STRING | Meaning not documented in the repo. |
| `u1` | STRING | Meaning not documented in the repo. |
| `u2` | STRING | Meaning not documented in the repo. |
| `u3` | STRING | Meaning not documented in the repo. |
| `d1` | STRING | Meaning not documented in the repo. |
| `d2` | STRING | Meaning not documented in the repo. |
| `d3` | STRING | Meaning not documented in the repo. |
| `sendto` | STRING | Meaning not documented in the repo. |
| `sendtime` | STRING | Meaning not documented in the repo. |
| `comment` | STRING | Meaning not documented in the repo. |
| `stktype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |

# How it is built

- Definition: `definitions/validated/mac5/tdis_approveqt.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tdis_approveqt](/initial/raw_mac5_ag01/tdis_approveqt.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY sendtime desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `docno`.
- Approximate size (BigQuery metadata, 2026-10-31): 416,890 rows, 39.0 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tdis_approveqt`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, docno, stktype, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tdis_approveqt`
GROUP BY company_id, docno, stktype
HAVING n > 1
```

---
type: BigQuery Table
title: "main_qtspread"
description: "One row = one quotation spread (main), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=main_qtspread&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: main_qtspread
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/main_qtspread.sqlx"
    title: "Dataform definition (validated/mac5/main_qtspread.sqlx)"
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

Validated copy of MAC5 `main_qtspread`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: quotation spread (main). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Surrogate identifier from the source system (the primary key). |
| `ref_id` | INT64 | Meaning not documented in the repo. |
| `qtid` | STRING | Meaning not documented in the repo. |
| `uinsert` | STRING | Meaning not documented in the repo. |
| `uupdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `dinsert` | DATETIME | Meaning not documented in the repo. |
| `dupdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `atten` | STRING | Meaning not documented in the repo. |
| `lat` | STRING | Meaning not documented in the repo. |
| `long` | STRING | Meaning not documented in the repo. |
| `mapnote` | STRING | Meaning not documented in the repo. |
| `city` | STRING | Meaning not documented in the repo. |
| `ctel` | STRING | Meaning not documented in the repo. |
| `ctel2` | STRING | Meaning not documented in the repo. |
| `road` | STRING | Meaning not documented in the repo. |
| `area` | STRING | Meaning not documented in the repo. |
| `district` | STRING | Meaning not documented in the repo. |
| `postcode` | STRING | Meaning not documented in the repo. |
| `caddress` | STRING | Meaning not documented in the repo. |
| `podocno` | STRING | Meaning not documented in the repo. |
| `rdosend` | STRING | Meaning not documented in the repo. |
| `checknote` | STRING | Meaning not documented in the repo. |
| `checknote2` | STRING | Meaning not documented in the repo. |
| `checknote3` | STRING | Meaning not documented in the repo. |
| `checknote4` | STRING | Meaning not documented in the repo. |
| `checknotemoney` | STRING | Meaning not documented in the repo. |
| `textnote` | STRING | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `editnote` | STRING | Meaning not documented in the repo. |
| `editnotedate` | DATETIME | Meaning not documented in the repo. |
| `delvdate` | STRING | Meaning not documented in the repo. |
| `transferfg` | STRING | Meaning not documented in the repo. |
| `meccode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `subcontract` | STRING | Meaning not documented in the repo. |
| `blueprint` | STRING | Meaning not documented in the repo. |
| `projectname` | STRING | Meaning not documented in the repo. |
| `mihjob` | STRING | Meaning not documented in the repo. |
| `repeatblueprint` | INT64 | Meaning not documented in the repo. |
| `noteblueprint` | STRING | Meaning not documented in the repo. |
| `discountthreepercent` | INT64 | Meaning not documented in the repo. |
| `paybycash` | INT64 | Meaning not documented in the repo. |
| `creditterm` | INT64 | Meaning not documented in the repo. |
| `moneydeposit` | FLOAT64 | Meaning not documented in the repo. |
| `extrasum` | INT64 | Meaning not documented in the repo. |
| `agent` | STRING | Meaning not documented in the repo. |
| `termpayment` | STRING | Meaning not documented in the repo. |
| `discountcash` | INT64 | Meaning not documented in the repo. |
| `paytype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `amount` | FLOAT64 | Meaning not documented in the repo. |
| `refer_order_allkons_m` | STRING | Meaning not documented in the repo. |
| `etax` | INT64 | Meaning not documented in the repo. |
| `etax_email` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/main_qtspread.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.main_qtspread](/initial/raw_mac5_ag01/main_qtspread.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY projectname desc, dupdate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 542,385 rows, 313.5 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.main_qtspread`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.main_qtspread`
GROUP BY company_id, id
HAVING n > 1
```

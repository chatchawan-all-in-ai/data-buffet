---
type: BigQuery Table
title: "mec"
description: "One row = one reference code table (mec), unique on (company_id, meccode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mec&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mec.sqlx"
    title: "Dataform definition (validated/mac5/mec.sqlx)"
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

Validated copy of MAC5 `mec`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: reference code table (mec). Table meaning is inferred from column prefixes.
Used by: [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md).

# Grain and key

One row per `company_id`, `meccode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `meccode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `mectpl` | INT64 | Meaning not documented in the repo. |
| `mectoctype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `mectocode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `mect1` | STRING | Meaning not documented in the repo. |
| `mect2` | STRING | Meaning not documented in the repo. |
| `mect3` | STRING | Meaning not documented in the repo. |
| `mect4` | STRING | Meaning not documented in the repo. |
| `mect5` | STRING | Meaning not documented in the repo. |
| `mecd1` | DATETIME | Meaning not documented in the repo. |
| `mecd2` | DATETIME | Meaning not documented in the repo. |
| `mecd3` | DATETIME | Meaning not documented in the repo. |
| `meci1` | INT64 | Meaning not documented in the repo. |
| `meci2` | INT64 | Meaning not documented in the repo. |
| `mecc1` | FLOAT64 | Meaning not documented in the repo. |
| `mecc2` | FLOAT64 | Meaning not documented in the repo. |
| `mecc3` | FLOAT64 | Meaning not documented in the repo. |
| `mecc4` | FLOAT64 | Meaning not documented in the repo. |
| `mecc5` | FLOAT64 | Meaning not documented in the repo. |
| `mecm1` | STRING | Meaning not documented in the repo. |
| `mecm2` | STRING | Meaning not documented in the repo. |
| `mecm3` | STRING | Meaning not documented in the repo. |
| `mecm4` | STRING | Meaning not documented in the repo. |
| `mecm5` | STRING | Meaning not documented in the repo. |
| `mecm6` | STRING | Meaning not documented in the repo. |
| `mecm7` | STRING | Meaning not documented in the repo. |
| `mecm8` | STRING | Meaning not documented in the repo. |
| `mecm9` | STRING | Meaning not documented in the repo. |
| `mecdesc` | STRING | Meaning not documented in the repo. |
| `mechide` | INT64 | Meaning not documented in the repo. |
| `meclock` | INT64 | Meaning not documented in the repo. |
| `meceditlk` | DATETIME | Meaning not documented in the repo. |
| `mecrefwe` | STRING | Meaning not documented in the repo. |
| `mecsortn` | STRING | Meaning not documented in the repo. |
| `mect6` | STRING | Meaning not documented in the repo. |
| `mect7` | STRING | Meaning not documented in the repo. |
| `mect8` | STRING | Meaning not documented in the repo. |
| `mect9` | STRING | Meaning not documented in the repo. |
| `mect10` | STRING | Meaning not documented in the repo. |
| `meceditdt` | DATETIME | Meaning not documented in the repo. |
| `meceditmf` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/mec.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mec](/initial/raw_mac5_ag01/mec.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY meceditdt desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `meccode`.
- Approximate size (BigQuery metadata, 2026-10-31): 11,608 rows, 2.7 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mec`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, meccode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mec`
GROUP BY company_id, meccode
HAVING n > 1
```

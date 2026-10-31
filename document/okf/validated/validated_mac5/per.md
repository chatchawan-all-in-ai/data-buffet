---
type: BigQuery Table
title: "per"
description: "One row = one personnel, unique on (company_id, percode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=per&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/per.sqlx"
    title: "Dataform definition (validated/mac5/per.sqlx)"
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

Validated copy of MAC5 `per` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: personnel. Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_order](/dimension/dim_order.md).

# Grain and key

One row per `company_id`, `percode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `percode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `perdep` | STRING | Meaning not documented in the repo. |
| `pertaxnos` | STRING | Meaning not documented in the repo. |
| `pernamet` | STRING | Meaning not documented in the repo. |
| `pernamee` | STRING | Meaning not documented in the repo. |
| `perbdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `perworks` | DATETIME | Meaning not documented in the repo. |
| `perworkf` | DATETIME | Meaning not documented in the repo. |
| `peradd1` | STRING | Meaning not documented in the repo. |
| `peradd2` | STRING | Meaning not documented in the repo. |
| `peradd3` | STRING | Meaning not documented in the repo. |
| `pertel` | STRING | Meaning not documented in the repo. |
| `perpositn` | STRING | Meaning not documented in the repo. |
| `perstatus` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |
| `pernchild` | INT64 | Meaning not documented in the repo. |
| `percisstudy` | INT64 | Meaning not documented in the repo. |
| `pernotstudy` | INT64 | Meaning not documented in the repo. |
| `persalary` | FLOAT64 | Meaning not documented in the repo. |
| `perhide` | INT64 | Meaning not documented in the repo. |
| `perlock` | INT64 | Meaning not documented in the repo. |
| `permemo` | STRING | Meaning not documented in the repo. |
| `pereditlk` | DATETIME | Meaning not documented in the repo. |
| `perrefwe` | STRING | Meaning not documented in the repo. |
| `pereditdt` | DATETIME | Meaning not documented in the repo. |
| `pereditmf` | STRING | Meaning not documented in the repo. |
| `perzone` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/per.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.per](/initial/raw_mac5_ag01/per.md), [raw_mac5_aa05.per](/initial/raw_mac5_aa05/per.md), [raw_mac5_ab01.per](/initial/raw_mac5_ab01/per.md), [raw_mac5_ac02.per](/initial/raw_mac5_ac02/per.md), [raw_mac5_ak02.per](/initial/raw_mac5_ak02/per.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY perbdate desc, pernamet desc, pernamee desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `percode`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,801 rows, 500.8 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.per`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, percode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.per`
GROUP BY company_id, percode
HAVING n > 1
```

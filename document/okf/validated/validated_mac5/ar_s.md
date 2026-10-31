---
type: BigQuery Table
title: "ar_s"
description: "One row = one AR status, unique on (company_id, ar_scode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=ar_s&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/ar_s.sqlx"
    title: "Dataform definition (validated/mac5/ar_s.sqlx)"
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

Validated copy of MAC5 `ar_s` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: AR status. Table meaning is inferred from column prefixes.
Used by: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [fact_view.view_fact_mir_rs](/view/fact_view/view_fact_mir_rs.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_order](/dimension/dim_order.md).

# Grain and key

One row per `company_id`, `ar_scode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `ar_scode` | INT64 | Likely code (inferred from the column name only; not documented in the repo). |
| `ar_snamet` | STRING | Meaning not documented in the repo. |
| `ar_snamee` | STRING | Meaning not documented in the repo. |
| `ar_scolf` | INT64 | Meaning not documented in the repo. |
| `ar_scolb` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/ar_s.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.ar_s](/initial/raw_mac5_ag01/ar_s.md), [raw_mac5_aa05.ar_s](/initial/raw_mac5_aa05/ar_s.md), [raw_mac5_ab01.ar_s](/initial/raw_mac5_ab01/ar_s.md), [raw_mac5_ac02.ar_s](/initial/raw_mac5_ac02/ar_s.md), [raw_mac5_ak02.ar_s](/initial/raw_mac5_ak02/ar_s.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ar_snamet desc, ar_snamee desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `ar_scode`.
- Approximate size (BigQuery metadata, 2026-10-31): 419 rows, 32.4 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.ar_s`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, ar_scode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.ar_s`
GROUP BY company_id, ar_scode
HAVING n > 1
```

---
type: BigQuery Table
title: "mir"
description: "One row = one receipt/return line (per company), unique on (company_id, mirtype, mirvnos, mirlistno)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mir&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mir.sqlx"
    title: "Dataform definition (validated/mac5/mir.sqlx)"
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

Validated copy of MAC5 `mir` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: receipt/return line (per company). Table meaning is inferred from column prefixes.
Used by: [fact_table.fact_mir_rs](/fact/fact_mir_rs.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row per `company_id`, `mirtype`, `mirvnos`, `mirlistno`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `mirday` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `mirmonth` | INT64 | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `miryear` | INT64 | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `mirtype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `mirvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `mircus` | STRING | Likely customer code (inferred from the column name only; not documented in the repo). |
| `mirlistno` | INT64 | Meaning not documented in the repo. |
| `mirbinvno` | STRING | Meaning not documented in the repo. |
| `mirbinvdate` | DATETIME | Meaning not documented in the repo. |
| `mirbinvtype` | STRING | Meaning not documented in the repo. |
| `mirdesc` | STRING | Meaning not documented in the repo. |
| `mircog` | FLOAT64 | Meaning not documented in the repo. |
| `mirvat` | FLOAT64 | Meaning not documented in the repo. |
| `mirsum` | FLOAT64 | Meaning not documented in the repo. |
| `mircurc` | INT64 | Meaning not documented in the repo. |
| `mirexchg` | FLOAT64 | Meaning not documented in the repo. |
| `mirtag` | INT64 | Meaning not documented in the repo. |
| `mirnotes` | STRING | Meaning not documented in the repo. |
| `miraccount` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mir.sqlx` (`type: "incremental"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mir](/initial/raw_mac5_ag01/mir.md), [raw_mac5_aa05.mir](/initial/raw_mac5_aa05/mir.md), [raw_mac5_ab01.mir](/initial/raw_mac5_ab01/mir.md), [raw_mac5_ac02.mir](/initial/raw_mac5_ac02/mir.md), [raw_mac5_ak02.mir](/initial/raw_mac5_ak02/mir.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY mirbinvdate desc, mirdesc desc) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `mirtype`, `mirvnos`, `mircus`.
- **Document-grain purge**: `pre_operations` builds a TEMP table of the batch and DELETEs whole documents (company_id + type + vnos) from the target before the MERGE, so lines deleted at source disappear.
- Approximate size (BigQuery metadata, 2026-10-31): 3,284,202 rows, 1.6 GB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mir`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, mirtype, mirvnos, mirlistno, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mir`
GROUP BY company_id, mirtype, mirvnos, mirlistno
HAVING n > 1
```

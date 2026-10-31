---
type: BigQuery Table
title: "cst"
description: "One row = one cost/stock transaction, unique on (company_id, CSTdate, CSTtype, CSTvnos, CSTcus, CSTstk, CSTsto, CSTio, CSTlist)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cst&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cst.sqlx"
    title: "Dataform definition (validated/mac5/cst.sqlx)"
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

Validated copy of MAC5 `cst`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: cost/stock transaction. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `CSTdate`, `CSTtype`, `CSTvnos`, `CSTcus`, `CSTstk`, `CSTsto`, `CSTio`, `CSTlist`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `cstdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `csttype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `cstvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `cstcus` | STRING | Likely customer code (inferred from the column name only; not documented in the repo). |
| `cststk` | STRING | Likely stock (SKU) code (inferred from the column name only; not documented in the repo). |
| `cstjob` | STRING | Meaning not documented in the repo. |
| `cstdep` | STRING | Meaning not documented in the repo. |
| `cstper` | STRING | Meaning not documented in the repo. |
| `cstdoc` | STRING | Meaning not documented in the repo. |
| `cstmec` | STRING | Meaning not documented in the repo. |
| `cststo` | STRING | Meaning not documented in the repo. |
| `cstquan` | FLOAT64 | Meaning not documented in the repo. |
| `cstquanp2` | FLOAT64 | Meaning not documented in the repo. |
| `cstcogsp` | FLOAT64 | Meaning not documented in the repo. |
| `cstexpdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `cstlinkvc` | STRING | Meaning not documented in the repo. |
| `cstlinkvcid` | INT64 | Meaning not documented in the repo. |
| `cstio` | INT64 | Meaning not documented in the repo. |
| `cstiozw` | INT64 | Meaning not documented in the repo. |
| `cstlist` | INT64 | Meaning not documented in the repo. |
| `cstcosta` | FLOAT64 | Meaning not documented in the repo. |
| `cstcostf` | FLOAT64 | Meaning not documented in the repo. |
| `cstcostl` | FLOAT64 | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/cst.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.cst](/initial/raw_mac5_ag01/cst.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `cstdate`, `cstcus`, `cststk`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,087,296 rows, 490.4 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cst`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, CSTdate, CSTtype, CSTvnos, CSTcus, CSTstk, CSTsto, CSTio, CSTlist, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cst`
GROUP BY company_id, CSTdate, CSTtype, CSTvnos, CSTcus, CSTstk, CSTsto, CSTio, CSTlist
HAVING n > 1
```

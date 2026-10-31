---
type: BigQuery Table
title: "cps"
description: "One row = one cost-per-stock movement, unique on (company_id, rowguid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cps&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cps.sqlx"
    title: "Dataform definition (validated/mac5/cps.sqlx)"
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

Validated copy of MAC5 `cps`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: cost-per-stock movement. Table meaning is inferred from column prefixes.
Used by: [fact_table.fact_backlog_store](/fact/fact_backlog_store.md).

# Grain and key

One row per `company_id`, `rowguid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `rowguid` | STRING | Meaning not documented in the repo. |
| `cpsstkid` | STRING | Meaning not documented in the repo. |
| `cpslinkid` | INT64 | Meaning not documented in the repo. |
| `cpsvnosid` | STRING | Meaning not documented in the repo. |
| `cpsdateid` | DATETIME | Meaning not documented in the repo. |
| `cpscusid` | STRING | Meaning not documented in the repo. |
| `cpsjob` | STRING | Meaning not documented in the repo. |
| `cpsdep` | STRING | Meaning not documented in the repo. |
| `cpsper` | STRING | Meaning not documented in the repo. |
| `cpsdoc` | STRING | Meaning not documented in the repo. |
| `cpsmec` | STRING | Meaning not documented in the repo. |
| `cpssto` | STRING | Meaning not documented in the repo. |
| `cpsstkreq` | FLOAT64 | Meaning not documented in the repo. |
| `cpsstkcut1` | FLOAT64 | Meaning not documented in the repo. |
| `cpsstkcut2` | FLOAT64 | Meaning not documented in the repo. |
| `cpssumreq` | FLOAT64 | Meaning not documented in the repo. |
| `cpssumcut1` | FLOAT64 | Meaning not documented in the repo. |
| `cpssumcut2` | FLOAT64 | Meaning not documented in the repo. |
| `cpsclearstk` | INT64 | Meaning not documented in the repo. |
| `cpsclearsum` | INT64 | Meaning not documented in the repo. |
| `cpsclearuser` | INT64 | Meaning not documented in the repo. |
| `cpsclearall` | INT64 | Meaning not documented in the repo. |
| `cpscurc` | INT64 | Meaning not documented in the repo. |
| `cpsexchg` | FLOAT64 | Meaning not documented in the repo. |
| `cpscut` | INT64 | Meaning not documented in the repo. |
| `cpsdelvdate` | DATETIME | Meaning not documented in the repo. |
| `cpslistno` | INT64 | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/cps.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.cps](/initial/raw_mac5_ag01/cps.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `rowguid`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,520,403 rows, 845.2 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cps`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, rowguid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cps`
GROUP BY company_id, rowguid
HAVING n > 1
```

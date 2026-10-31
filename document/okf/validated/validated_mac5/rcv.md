---
type: BigQuery Table
title: "rcv"
description: "One row = one receiving / goods receipt, unique on (company_id, serial)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=rcv&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/rcv.sqlx"
    title: "Dataform definition (validated/mac5/rcv.sqlx)"
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

Validated copy of MAC5 `rcv`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: receiving / goods receipt. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `serial`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `serial` | STRING | Meaning not documented in the repo. |
| `rcvdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `rcvtype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `rcvvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `rcvstk` | STRING | Likely stock (SKU) code (inferred from the column name only; not documented in the repo). |
| `desct1` | STRING | Meaning not documented in the repo. |
| `qty` | STRING | Likely quantity (inferred from the column name only; not documented in the repo). |
| `unit` | STRING | Meaning not documented in the repo. |
| `rcvsto` | STRING | Meaning not documented in the repo. |
| `username` | STRING | Meaning not documented in the repo. |
| `remark` | STRING | Likely free-text remark (inferred from the column name only; not documented in the repo). |
| `rcvtime` | STRING | Meaning not documented in the repo. |
| `fdatetime2` | STRING | Meaning not documented in the repo. |
| `rcvstatus` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `rcvtypefg` | STRING | Meaning not documented in the repo. |
| `rcvstatusmr` | STRING | Meaning not documented in the repo. |
| `rcvzone` | STRING | Meaning not documented in the repo. |
| `rcvorder` | STRING | Meaning not documented in the repo. |
| `rcvcommand` | STRING | Meaning not documented in the repo. |
| `rcvextcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `mixvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `mixdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `rcvtrancode` | STRING | Meaning not documented in the repo. |
| `rcvcancel` | INT64 | Likely cancel flag (inferred from the column name only; not documented in the repo). |
| `rcvorder_pack` | STRING | Meaning not documented in the repo. |
| `adjvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `packdate` | STRING | Meaning not documented in the repo. |
| `packtime` | STRING | Meaning not documented in the repo. |
| `rcvconvert` | INT64 | Meaning not documented in the repo. |
| `odate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `ouser` | STRING | Meaning not documented in the repo. |
| `fmil2listno` | INT64 | Meaning not documented in the repo. |
| `ostatus` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/rcv.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.rcv](/initial/raw_mac5_ag01/rcv.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `serial`.
- Approximate size (BigQuery metadata, 2026-10-31): 0 rows, 0 B.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.rcv`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, serial, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.rcv`
GROUP BY company_id, serial
HAVING n > 1
```

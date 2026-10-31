---
type: BigQuery Table
title: "cpx"
description: "One row = one reference code table (cpx), unique on (company_id, cpxstkid, cpxlinkid, cpxvnosid, cpxdateid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cpx&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cpx
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cpx.sqlx"
    title: "Dataform definition (validated/mac5/cpx.sqlx)"
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

Validated copy of MAC5 `cpx`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: reference code table (cpx). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `cpxstkid`, `cpxlinkid`, `cpxvnosid`, `cpxdateid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `cpxstkid` | STRING | Meaning not documented in the repo. |
| `cpxlinkid` | INT64 | Meaning not documented in the repo. |
| `cpxvnosid` | STRING | Meaning not documented in the repo. |
| `cpxdateid` | DATETIME | Meaning not documented in the repo. |
| `cpxjob` | STRING | Meaning not documented in the repo. |
| `cpxdep` | STRING | Meaning not documented in the repo. |
| `cpxper` | STRING | Meaning not documented in the repo. |
| `cpxdoc` | STRING | Meaning not documented in the repo. |
| `cpxmec` | STRING | Meaning not documented in the repo. |
| `cpxsto` | STRING | Meaning not documented in the repo. |
| `cpxstkreq` | FLOAT64 | Meaning not documented in the repo. |
| `cpxstkcut` | FLOAT64 | Meaning not documented in the repo. |
| `cpxclearstk` | INT64 | Meaning not documented in the repo. |
| `cpxclearuser` | INT64 | Meaning not documented in the repo. |
| `cpxclearall` | INT64 | Meaning not documented in the repo. |
| `cpxstatus` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |

# How it is built

- Definition: `definitions/validated/mac5/cpx.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.cpx](/initial/raw_mac5_ag01/cpx.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY cpxdateid desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `cpxstkid`.
- Approximate size (BigQuery metadata, 2026-10-31): 146,847 rows, 15.1 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cpx`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, cpxstkid, cpxlinkid, cpxvnosid, cpxdateid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cpx`
GROUP BY company_id, cpxstkid, cpxlinkid, cpxvnosid, cpxdateid
HAVING n > 1
```

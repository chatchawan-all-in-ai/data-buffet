---
type: BigQuery Table
title: "cfs"
description: "One row = one cashflow, unique on (company_id, cfsvnosid, cfsdateid, cfscusid, cfstypeid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cfs&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cfs
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cfs.sqlx"
    title: "Dataform definition (validated/mac5/cfs.sqlx)"
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

Validated copy of MAC5 `cfs` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: cashflow. Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md).

# Grain and key

One row per `company_id`, `cfsvnosid`, `cfsdateid`, `cfscusid`, `cfstypeid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `cfsvnosid` | STRING | Meaning not documented in the repo. |
| `cfsdateid` | DATETIME | Meaning not documented in the repo. |
| `cfscusid` | STRING | Meaning not documented in the repo. |
| `cfstypeid` | STRING | Meaning not documented in the repo. |
| `cfsjob` | STRING | Meaning not documented in the repo. |
| `cfsdep` | STRING | Meaning not documented in the repo. |
| `cfsper` | STRING | Meaning not documented in the repo. |
| `cfsdoc` | STRING | Meaning not documented in the repo. |
| `cfsmec` | STRING | Meaning not documented in the repo. |
| `cfssumreq` | FLOAT64 | Meaning not documented in the repo. |
| `cfssumcut1` | FLOAT64 | Meaning not documented in the repo. |
| `cfssumcut2` | FLOAT64 | Meaning not documented in the repo. |
| `cfsclearsum` | INT64 | Meaning not documented in the repo. |
| `cfsclearuser` | INT64 | Meaning not documented in the repo. |
| `cfsclearall` | INT64 | Meaning not documented in the repo. |
| `cfscurc` | INT64 | Meaning not documented in the repo. |
| `cfsexchg` | FLOAT64 | Meaning not documented in the repo. |
| `cfsbillcut` | FLOAT64 | Meaning not documented in the repo. |
| `cfsbillclr` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/cfs.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.cfs](/initial/raw_mac5_ag01/cfs.md), [raw_mac5_aa05.cfs](/initial/raw_mac5_aa05/cfs.md), [raw_mac5_ab01.cfs](/initial/raw_mac5_ab01/cfs.md), [raw_mac5_ac02.cfs](/initial/raw_mac5_ac02/cfs.md), [raw_mac5_ak02.cfs](/initial/raw_mac5_ak02/cfs.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY cfsdateid desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `cfsvnosid`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,667,276 rows, 229.0 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cfs`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, cfsvnosid, cfsdateid, cfscusid, cfstypeid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cfs`
GROUP BY company_id, cfsvnosid, cfsdateid, cfscusid, cfstypeid
HAVING n > 1
```

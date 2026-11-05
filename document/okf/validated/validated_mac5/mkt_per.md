---
type: BigQuery Table
title: "mkt_per"
description: "One row = one salesperson in the marketing roster (per company), unique on (company_id, percode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mkt_per&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mkt_per
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mkt_per.sqlx"
    title: "Dataform definition (validated/mac5/mkt_per.sqlx)"
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

Validated copy of MAC5 `mkt_per`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Salesperson roster used by marketing, with name, zone and assignment period.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `percode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `percode` | STRING | Salesperson (employee) code. |
| `pername` | STRING | Salesperson name. |
| `perstart` | DATETIME | Start date of the salesperson's marketing assignment. |
| `perend` | DATETIME | End date of the salesperson's marketing assignment. |
| `perzone` | STRING | Sales zone of the salesperson (e.g. `M/T`, Northeast in Thai). |
| `persector` | STRING | Sales sector of the salesperson. |
| `zseq` | INT64 | Sequence number of the assignment. |

# How it is built

- Definition: `definitions/validated/mac5/mkt_per.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mkt_per](/initial/raw_mac5_ag01/mkt_per.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY perstart desc, perend desc, pername desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `percode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mkt_per`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, percode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mkt_per`
GROUP BY company_id, percode
HAVING n > 1
```

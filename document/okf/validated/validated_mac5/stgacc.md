---
type: BigQuery Table
title: "stgacc"
description: "One row = one accounting product group (per company), unique on (company_id, gacccode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stgacc&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: stgacc
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stgacc.sqlx"
    title: "Dataform definition (validated/mac5/stgacc.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `stgacc`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Accounting product groups (code and name) used to map stock groups to accounting groups.

Read by: [validated_mac5.stg](/validated/validated_mac5/stg.md).

# Grain and key

One row per `company_id`, `gacccode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `gacccode` | STRING | Accounting product group code (e.g. `02BI`). |
| `gaccname` | STRING | Accounting product group name. |

# How it is built

- Definition: `definitions/validated/mac5/stgacc.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.stgacc](/initial/raw_mac5_ag01/stgacc.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY gaccname desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `gacccode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stgacc`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, gacccode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stgacc`
GROUP BY company_id, gacccode
HAVING n > 1
```

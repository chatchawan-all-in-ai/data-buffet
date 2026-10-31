---
type: BigQuery Table
title: "tmp_mihstatus"
description: "One row = one cleaned source record of `tmp_mihstatus` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tmp_mihstatus&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tmp_mihstatus
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tmp_mihstatus.sqlx"
    title: "Dataform definition (validated/mac5/tmp_mihstatus.sqlx)"
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

Validated copy of MAC5 `tmp_mihstatus`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: temporary document status. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `mihvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `mihstatus` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `sdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |

# How it is built

- Definition: `definitions/validated/mac5/tmp_mihstatus.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tmp_mihstatus](/initial/raw_mac5_ag01/tmp_mihstatus.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `mihvnos`.
- Approximate size (BigQuery metadata, 2026-10-31): 246,606 rows, 10.2 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tmp_mihstatus`
LIMIT 100
```

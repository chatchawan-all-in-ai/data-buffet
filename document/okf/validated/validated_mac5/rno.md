---
type: BigQuery Table
title: "rno"
description: "One row = one cleaned source record of `rno` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=rno&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/rno.sqlx"
    title: "Dataform definition (validated/mac5/rno.sqlx)"
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

Validated copy of MAC5 `rno`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: running number reference. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `rnoid` | INT64 | Meaning not documented in the repo. |
| `rnoprefix` | STRING | Meaning not documented in the repo. |
| `rnoyear` | STRING | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `rnomonth` | STRING | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `rnorunning` | INT64 | Meaning not documented in the repo. |
| `rnorunno` | STRING | Meaning not documented in the repo. |
| `rnocrdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `rnoupdatedate` | DATETIME | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/rno.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.rno](/initial/raw_mac5_ag01/rno.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `rnoid`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,509 rows, 90.9 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.rno`
LIMIT 100
```

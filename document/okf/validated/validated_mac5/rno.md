---
type: BigQuery Table
title: "rno"
description: "One row = one document running-number sequence for one prefix and period from source table `rno` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=rno&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: rno
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

Validated copy of MAC5 `rno`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Running-number sequences per document prefix and year/month, with the last number issued.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `rnoid` | INT64 | Running ID of the running-number row. |
| `rnoprefix` | STRING | Document number prefix of the sequence (e.g. RTM, RCM, PCM). |
| `rnoyear` | STRING | Two-digit Buddhist-era year of the sequence (e.g. `58` = 2015). |
| `rnomonth` | STRING | Two-digit month of the sequence. |
| `rnorunning` | INT64 | Last running number used in the sequence. |
| `rnorunno` | STRING | Last full document number issued in the sequence. |
| `rnocrdate` | DATETIME | Date and time the sequence row was created. |
| `rnoupdatedate` | DATETIME | Date and time the sequence row was last updated. |

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

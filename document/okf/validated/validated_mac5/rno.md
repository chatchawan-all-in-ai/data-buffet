---
type: BigQuery Table
title: "rno"
description: "One row = one document running-number sequence for one prefix and period from source table `rno`."
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
generated: { by: "agent:codex", at: "2026-11-09T02:15:58+00:00" }
status: draft
---

# What it is

Validated copy of MAC5 `rno`: every column is trimmed/cast with the shared helpers. There is no business logic at this layer. Table meaning: Running-number sequences per document prefix and year/month, with the last number issued.
No other repo object reads it.

# Grain and key

One row per `company_id`, `rnoid`. `uniqueKey` and `pk_key` declare this key; `QUALIFY ROW_NUMBER()` keeps the first row ordered by `rnoupdatedate desc`. Each full rebuild attaches a `NOT ENFORCED` primary key using the standard retry loop.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
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
- Storage: not partitioned; cluster by `company_id`, `rnoid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.rno`
LIMIT 100
```

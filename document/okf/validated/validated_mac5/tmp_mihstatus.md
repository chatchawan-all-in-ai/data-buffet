---
type: BigQuery Table
title: "tmp_mihstatus"
description: "One row = one sales document status snapshot from source table `tmp_mihstatus`."
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
generated: { by: "agent:codex", at: "2026-11-09T02:15:58+00:00" }
status: draft
---

# What it is

Validated copy of MAC5 `tmp_mihstatus`: every column is trimmed/cast with the shared helpers. There is no business logic at this layer. Table meaning: Status codes of MAC5 sales documents with the time each status was recorded.
No other repo object reads it.

# Grain and key

One row per `company_id`, `mihvnos`, `mihstatus`, `sdate`. `uniqueKey` and `pk_key` declare this key; `QUALIFY ROW_NUMBER()` keeps the first row ordered by `sdate desc`. Each full rebuild attaches a `NOT ENFORCED` primary key using the standard retry loop. Missing or blank string key components are cleaned to the empty string.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `mihvnos` | STRING | Document number, unique within company and document type. |
| `mihstatus` | STRING | Document status code; meaning in `ar_s` for sales types and `ap_s` for purchase types (e.g. 26 = approved sales order, 30 = VAT sale, 32 = cancelled tax invoice). |
| `sdate` | STRING | Date and time the status was recorded (text such as `Nov 25 2025  9:49PM`). |

# How it is built

- Definition: `definitions/validated/mac5/tmp_mihstatus.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tmp_mihstatus](/initial/raw_mac5_ag01/tmp_mihstatus.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: not partitioned; cluster by `company_id`, `mihvnos`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tmp_mihstatus`
LIMIT 100
```

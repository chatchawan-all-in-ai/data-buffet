---
type: BigQuery Table
title: "tbook_payin"
description: "One row = one pay-in record of a sales order from source table `tbook_payin` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_payin&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbook_payin
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_payin.sqlx"
    title: "Dataform definition (validated/mac5/tbook_payin.sqlx)"
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

Validated copy of MAC5 `tbook_payin`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Pay-in submissions of sales orders with status and approval time.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `orderno` | STRING | MAC5 sales order number the pay-in belongs to. |
| `status` | INT64 | Pay-in status code (0 to 6). |
| `datetime` | DATETIME | Date and time the pay-in was submitted. |
| `datetimeapprove` | DATETIME | Date and time the pay-in was approved. |

# How it is built

- Definition: `definitions/validated/mac5/tbook_payin.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_payin](/initial/raw_mac5_ag01/tbook_payin.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `orderno`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_payin`
LIMIT 100
```

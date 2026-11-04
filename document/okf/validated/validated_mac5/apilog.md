---
type: BigQuery Table
title: "apilog"
description: "One row = one API job run (per company), unique on (company_id, logid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=apilog&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: apilog
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/apilog.sqlx"
    title: "Dataform definition (validated/mac5/apilog.sqlx)"
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

Validated copy of MAC5 `apilog`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Run log of the API job that processes Allkons orders, with start and end time, success flag, message and processed orders.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `logid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `logid` | INT64 | Run identifier of the API job. |
| `runat` | DATETIME | Date and time the API run started. |
| `completedat` | DATETIME | Date and time the API run finished. |
| `issuccess` | INT64 | Success flag of the run (1 = success, 0 = failed). |
| `errormessage` | STRING | Error or status message of the run (e.g. `Batch is null - no orders to process.`). |
| `resultjson` | STRING | JSON array of the orders processed in the run, keyed by Allkons billing number. |

# How it is built

- Definition: `definitions/validated/mac5/apilog.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.apilog](/initial/raw_mac5_ag01/apilog.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY completedat desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `logid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.apilog`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, logid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.apilog`
GROUP BY company_id, logid
HAVING n > 1
```

---
type: BigQuery Table
title: "tab"
description: "One row = one link between a document line and its source document line from source table `tab`, unique on (company_id, tabvnosid, tabdateid, tabcusid, tabtypeid, tablistno)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tab&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tab
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tab.sqlx"
    title: "Dataform definition (validated/mac5/tab.sqlx)"
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

Validated copy of MAC5 `tab`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Links from invoice lines to the sales-order lines they were drawn from, with quantity and amount taken.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `tabvnosid`, `tabdateid`, `tabcusid`, `tabtypeid`, `tablistno`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `tabvnosid` | STRING | Document number of the document (e.g. invoice number). |
| `tabdateid` | DATETIME | Document date. |
| `tabcusid` | STRING | Customer code of the document. |
| `tabtypeid` | STRING | Document type code (e.g. `IS` = invoice). |
| `tablinktype` | STRING | Link type code of the row. |
| `tablinkvno` | STRING | Document number of the linked source document (e.g. sales order). |
| `tablinkvdate` | DATETIME | Date of the linked source document. |
| `tablinkvcus` | STRING | Customer code of the linked source document. |
| `tablinkvtype` | STRING | Document type code of the linked source document (e.g. `PS` = sales order). |
| `tablinkvid` | INT64 | Line ID of the linked source document line. |
| `tabstk` | STRING | Stock code of the linked line. |
| `tabquan` | FLOAT64 | Quantity taken from the linked line. |
| `tabquanp2` | FLOAT64 | Quantity taken from the linked line, in the second unit. |
| `tabsum` | FLOAT64 | Amount taken from the linked line. |
| `tabcurc` | INT64 | Currency code (0 = baht). |
| `tabexchg` | FLOAT64 | Exchange rate (1.0 = baht). |
| `tablistno` | INT64 | Line number within the document. |

# How it is built

- Definition: `definitions/validated/mac5/tab.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tab](/initial/raw_mac5_ag01/tab.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY tabdateid desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `tabvnosid`, `tabdateid`, `tabcusid`.
- Approximate size (BigQuery metadata, 2026-10-31): 4,577,141 rows, 603.6 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tab`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, tabvnosid, tabdateid, tabcusid, tabtypeid, tablistno, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tab`
GROUP BY company_id, tabvnosid, tabdateid, tabcusid, tabtypeid, tablistno
HAVING n > 1
```

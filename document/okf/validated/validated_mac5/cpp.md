---
type: BigQuery Table
title: "cpp"
description: "One row = one outstanding purchase order line (per company), unique on (company_id, rowguid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cpp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cpp
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cpp.sqlx"
    title: "Dataform definition (validated/mac5/cpp.sqlx)"
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

Validated copy of MAC5 `cpp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Outstanding purchase order lines: ordered versus received quantity and amount, with clearing flags.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `rowguid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |
| `cppstkid` | STRING | Product (stock) code of the outstanding purchase line, matching `stk.stkcode`. |
| `cpplinkid` | INT64 | Internal ID linking the outstanding record to its document line. |
| `cppvnosid` | STRING | Number of the purchase order document that has the outstanding line (e.g. a `POF...` purchase order). |
| `cppdateid` | DATETIME | Date of the purchase order document. |
| `cppcusid` | STRING | Supplier code of the document, matching `cre.crecode`. |
| `cppjob` | STRING | Job code of the document (sales job or project category). |
| `cppdep` | STRING | Department code of the document, used as the sales channel code. |
| `cppper` | STRING | Purchaser (employee) code of the document. |
| `cppdoc` | STRING | Document reference code. |
| `cppmec` | STRING | Memo-card code of the document, matching `mec.meccode`. |
| `cppsto` | STRING | Warehouse (store) code the line is received into. |
| `cppstkreq` | FLOAT64 | Quantity ordered on the purchase line. |
| `cppstkcut1` | FLOAT64 | Quantity already received against the purchase line. |
| `cppstkcut2` | FLOAT64 | Quantity cut against the line by adjustment documents. |
| `cppsumreq` | FLOAT64 | Amount ordered on the line. |
| `cppsumcut1` | FLOAT64 | Amount already received or invoiced against the purchase line. |
| `cppsumcut2` | FLOAT64 | Amount cut against the line by adjustment documents. |
| `cppclearstk` | INT64 | Flag: outstanding quantity cleared (-1 = cleared). |
| `cppclearsum` | INT64 | Flag: outstanding amount cleared (-1 = cleared). |
| `cppclearuser` | INT64 | Flag: line cleared manually by a user (-1 = yes). |
| `cppclearall` | INT64 | Flag: line fully cleared (-1 = cleared). |
| `cppcurc` | INT64 | Currency code (0 = Thai baht). |
| `cppexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `cppcut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `cppdelvdate` | DATETIME | Expected delivery date of the purchase line. |
| `cpplistno` | INT64 | Line number within the document. |

# How it is built

- Definition: `definitions/validated/mac5/cpp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.cpp](/initial/raw_mac5_ag01/cpp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY cppdateid desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `rowguid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cpp`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, rowguid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cpp`
GROUP BY company_id, rowguid
HAVING n > 1
```

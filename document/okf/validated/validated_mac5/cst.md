---
type: BigQuery Table
title: "cst"
description: "One row = one cost line of one stock document line (per company), unique on (company_id, CSTdate, CSTtype, CSTvnos, CSTcus, CSTstk, CSTsto, CSTio, CSTlist)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cst&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cst
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cst.sqlx"
    title: "Dataform definition (validated/mac5/cst.sqlx)"
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

Validated copy of MAC5 `cst`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Cost-of-goods lines per document line (invoices, sales orders), with quantity, warehouse, salesperson and COGS.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `CSTdate`, `CSTtype`, `CSTvnos`, `CSTcus`, `CSTstk`, `CSTsto`, `CSTio`, `CSTlist`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `cstdate` | DATETIME | Document date. |
| `csttype` | STRING | Document type code (IS = invoice, PS = sales order). |
| `cstvnos` | STRING | Document number. |
| `cstcus` | STRING | Customer code (joins `deb.debcode`). |
| `cststk` | STRING | Stock code of the line (joins `stk.stkcode`). |
| `cstjob` | STRING | Job code of the line. |
| `cstdep` | STRING | Department code of the line. |
| `cstper` | STRING | Salesperson code of the line (joins `per.percode`). |
| `cstdoc` | STRING | Document reference code of the line. |
| `cstmec` | STRING | Branch (mec) code of the document. |
| `cststo` | STRING | Warehouse code of the line (joins `sto.stocode`). |
| `cstquan` | FLOAT64 | Quantity in the base unit. |
| `cstquanp2` | FLOAT64 | Quantity in the second unit. |
| `cstcogsp` | FLOAT64 | Cost of goods sold of the line in baht. |
| `cstexpdate` | DATETIME | Expiry date of the item on the line. |
| `cstlinkvc` | STRING | Document type code of the linked source document (e.g. `PS` = sales order). |
| `cstlinkvcid` | INT64 | Line ID of the linked source document line. |
| `cstio` | INT64 | Stock in/out direction code (0, 2). |
| `cstiozw` | INT64 | Stock movement kind code (0, 5). |
| `cstlist` | INT64 | Line number within the document. |
| `cstcosta` | FLOAT64 | Average-cost flag of the line (-1 = yes, 0 = no). |
| `cstcostf` | FLOAT64 | FIFO-cost flag of the line (-1 = yes, 0 = no). |
| `cstcostl` | FLOAT64 | LIFO-cost flag of the line (-1 = yes, 0 = no). |
| `asatdate` | DATE | Extract (snapshot) date of the source file, taken from the `ASATDATE` partition. |

# How it is built

- Definition: `definitions/validated/mac5/cst.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.cst](/initial/raw_mac5_ag01/cst.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `cstdate`, `cstcus`, `cststk`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,087,296 rows, 490.4 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cst`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, CSTdate, CSTtype, CSTvnos, CSTcus, CSTstk, CSTsto, CSTio, CSTlist, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cst`
GROUP BY company_id, CSTdate, CSTtype, CSTvnos, CSTcus, CSTstk, CSTsto, CSTio, CSTlist
HAVING n > 1
```

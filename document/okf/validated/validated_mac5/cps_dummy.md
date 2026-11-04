---
type: BigQuery Table
title: "cps_dummy"
description: "One row = one outstanding sales order line (per company), unique on (company_id, rowguid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cps_dummy&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cps_dummy
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cps_dummy.sqlx"
    title: "Dataform definition (validated/mac5/cps_dummy.sqlx)"
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

Validated copy of MAC5 `cps_dummy`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Outstanding sales order lines from the ERP's dummy (staging) table, same layout as `cps`.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `rowguid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |
| `cpsstkid` | STRING | Product (stock) code of the outstanding line, matching `stk.stkcode`. |
| `cpslinkid` | INT64 | Internal ID linking the outstanding record to its document line. |
| `cpsvnosid` | STRING | Number of the sales order document that has the outstanding line (e.g. a `PS` sales order). |
| `cpsdateid` | DATETIME | Date of the sales order document. |
| `cpscusid` | STRING | Customer code of the document, matching `deb.debcode`. |
| `cpsjob` | STRING | Job code of the document (sales job or project category). |
| `cpsdep` | STRING | Department code of the document, used as the sales channel code. |
| `cpsper` | STRING | Salesperson (employee) code of the document. |
| `cpsdoc` | STRING | Document reference code. |
| `cpsmec` | STRING | Memo-card code of the document, matching `mec.meccode`. |
| `cpssto` | STRING | Warehouse (store) code the line is issued from or received into. |
| `cpsstkreq` | FLOAT64 | Quantity ordered on the line. |
| `cpsstkcut1` | FLOAT64 | Quantity already delivered or received against the line. |
| `cpsstkcut2` | FLOAT64 | Quantity cut against the line by adjustment documents. |
| `cpssumreq` | FLOAT64 | Amount ordered on the line. |
| `cpssumcut1` | FLOAT64 | Amount already delivered or invoiced against the line. |
| `cpssumcut2` | FLOAT64 | Amount cut against the line by adjustment documents. |
| `cpsclearstk` | INT64 | Flag: outstanding quantity cleared (-1 = cleared). |
| `cpsclearsum` | INT64 | Flag: outstanding amount cleared (-1 = cleared). |
| `cpsclearuser` | INT64 | Flag: line cleared manually by a user (-1 = yes). |
| `cpsclearall` | INT64 | Flag: line fully cleared (-1 = cleared). |
| `cpscurc` | INT64 | Currency code (0 = Thai baht). |
| `cpsexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `cpscut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `cpsdelvdate` | DATETIME | Requested delivery date of the line. |
| `cpslistno` | INT64 | Line number within the document. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/cps_dummy.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.cps_dummy](/initial/raw_mac5_ag01/cps_dummy.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `rowguid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cps_dummy`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, rowguid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cps_dummy`
GROUP BY company_id, rowguid
HAVING n > 1
```

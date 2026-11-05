---
type: BigQuery Table
title: "cql"
description: "One row = one cheque ledger entry (per company), unique on (company_id, cqlbank, cqlno, cqlsys, cqlday, cqlmonth, cqlyear, cqlautono)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cql&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cql
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cql.sqlx"
    title: "Dataform definition (validated/mac5/cql.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:28:26+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `cql` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Cheque and bank-book ledger entries linking each cheque to the receipt or payment document it settles. Cheque/receipt linkage is evidenced by [fact_chq](/fact/fact_chq.md): it matches cqlno to the cheque number, cqlcus to the customer and cqlsuml to the cheque amount, then exposes cqlvnos as the receipt number. Quotation detail instead comes from [tbook_quodetail](/validated/validated_mac5/tbook_quodetail.md).

Read by: [fact_table.fact_chq](/fact/fact_chq.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [pub_sub.export_chqri](/view/pub_sub/export_chqri.md), [pub_sub.export_receipt](/view/pub_sub/export_receipt.md).

# Grain and key

One row per `company_id`, `cqlbank`, `cqlno`, `cqlsys`, `cqlday`, `cqlmonth`, `cqlyear`, `cqlautono`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `cqldate` | DATETIME | Date of the cheque ledger entry. |
| `cqlbank` | STRING | Bank code of the cheque (e.g. `BBL`, `KBANK`). |
| `cqlno` | STRING | Cheque number, matching `chq.chqno`. |
| `cqlsys` | INT64 | Source system of the entry (1 = bank book, 2 = receipt or payment document). |
| `cqlday` | INT64 | Day part of the entry date. |
| `cqlmonth` | INT64 | Month part of the entry date. |
| `cqlyear` | INT64 | Year part of the entry date (Gregorian). |
| `cqlbook` | INT64 | Bank book number (0 = entry linked to a receipt or payment document). |
| `cqlvnos` | STRING | Number of the receipt or payment document the cheque settles (e.g. `RI-...`). |
| `cqlsuml` | FLOAT64 | Cheque amount of the entry. |
| `cqlmivt` | STRING | Document type of the linked document (RS = receipt, RP = payment, `--` = none). |
| `cqlcus` | STRING | Customer code (supplier code for payments), matching `deb.debcode`. |
| `cqltag` | INT64 | Tag marker of the entry. |
| `cqlautono` | INT64 | Auto-increment ID of the entry. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/cql.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.cql](/initial/raw_mac5_ag01/cql.md), [raw_mac5_aa05.cql](/initial/raw_mac5_aa05/cql.md), [raw_mac5_ab01.cql](/initial/raw_mac5_ab01/cql.md), [raw_mac5_ac02.cql](/initial/raw_mac5_ac02/cql.md), [raw_mac5_ak02.cql](/initial/raw_mac5_ak02/cql.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `cqlbank`, `cqlyear`, `cqlmonth`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cql`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, cqlbank, cqlno, cqlsys, cqlday, cqlmonth, cqlyear, cqlautono, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cql`
GROUP BY company_id, cqlbank, cqlno, cqlsys, cqlday, cqlmonth, cqlyear, cqlautono
HAVING n > 1
```

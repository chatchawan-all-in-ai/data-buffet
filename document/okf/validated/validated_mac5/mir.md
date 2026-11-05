---
type: BigQuery Table
title: "mir"
description: "One row = one receipt or billing statement line (per company), unique on (company_id, mirtype, mirvnos, mirlistno)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mir&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mir
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mir.sqlx"
    title: "Dataform definition (validated/mac5/mir.sqlx)"
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

Validated copy of MAC5 `mir` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Lines of receipts (`RS`/`RP`) and billing statements (`VS`/`VP`), each settling or billing one invoice or note.
Used by: [fact_table.fact_mir_rs](/fact/fact_mir_rs.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [pub_sub.export_receipt](/view/pub_sub/export_receipt.md).

# Grain and key

One row per `company_id`, `mirtype`, `mirvnos`, `mirlistno`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `mirday` | INT64 | Day part of the document date. |
| `mirmonth` | INT64 | Month part of the document date. |
| `miryear` | INT64 | Year part of the document date (Gregorian). |
| `mirtype` | STRING | Document type code (RS = sales receipt, VS = sales billing statement; RP / VP on the purchase side). |
| `mirvnos` | STRING | Receipt or billing-statement document number. |
| `mircus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `mirlistno` | INT64 | Line number within the receipt or billing statement. |
| `mirbinvno` | STRING | Number of the invoice (or debit/credit note) settled or billed by this line. |
| `mirbinvdate` | DATETIME | Date of the invoice settled or billed by this line. |
| `mirbinvtype` | STRING | Document type of the invoice settled or billed by this line (IS, AS, BS). |
| `mirdesc` | STRING | Description copied from the referenced invoice. |
| `mircog` | FLOAT64 | Line amount excluding VAT. |
| `mirvat` | FLOAT64 | VAT amount of the line. |
| `mirsum` | FLOAT64 | Line amount including VAT (amount received or billed). |
| `mircurc` | INT64 | Currency code (0 = Thai baht). |
| `mirexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `mirtag` | INT64 | Tag marker of the line. |
| `mirnotes` | STRING | Notes copied from the referenced invoice. |
| `miraccount` | STRING | Account code of the line. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mir.sqlx` (`type: "incremental"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mir](/initial/raw_mac5_ag01/mir.md), [raw_mac5_aa05.mir](/initial/raw_mac5_aa05/mir.md), [raw_mac5_ab01.mir](/initial/raw_mac5_ab01/mir.md), [raw_mac5_ac02.mir](/initial/raw_mac5_ac02/mir.md), [raw_mac5_ak02.mir](/initial/raw_mac5_ak02/mir.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY mirbinvdate desc, mirdesc desc) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `mirtype`, `mirvnos`, `mircus`.
- **Document-grain purge**: `pre_operations` builds a TEMP table of the batch and DELETEs whole documents (company_id + type + vnos) from the target before the MERGE, so lines deleted at source disappear.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mir`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, mirtype, mirvnos, mirlistno, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mir`
GROUP BY company_id, mirtype, mirvnos, mirlistno
HAVING n > 1
```

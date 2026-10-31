---
type: BigQuery Table
title: "cql"
description: "One row = one MAC5 cheque/receipt linkage record (per company), unique on (company_id, cqlbank, cqlno, cqlsys, cqlday, cqlmonth, cqlyear, cqlautono)."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `cql` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Cheque/receipt linkage is evidenced by [fact_chq](/fact/fact_chq.md): it matches cqlno to the cheque number, cqlcus to the customer and cqlsuml to the cheque amount, then exposes cqlvnos as the receipt number. Quotation detail instead comes from [tbook_quodetail](/validated/validated_mac5/tbook_quodetail.md).
Used by: [fact_table.fact_chq](/fact/fact_chq.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row per `company_id`, `cqlbank`, `cqlno`, `cqlsys`, `cqlday`, `cqlmonth`, `cqlyear`, `cqlautono`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `cqldate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `cqlbank` | STRING | Meaning not documented in the repo. |
| `cqlno` | STRING | Cheque number matched to chq.chqno by fact_chq. |
| `cqlsys` | INT64 | Meaning not documented in the repo. |
| `cqlday` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `cqlmonth` | INT64 | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `cqlyear` | INT64 | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `cqlbook` | INT64 | Meaning not documented in the repo. |
| `cqlvnos` | STRING | Receipt document number exposed by fact_chq and matched to RS mirvnos in fact_mir_rs. |
| `cqlsuml` | FLOAT64 | Amount matched to chq.chqtotal by fact_chq. |
| `cqlmivt` | STRING | Meaning not documented in the repo. |
| `cqlcus` | STRING | Customer code matched to chq.chqcus by fact_chq. |
| `cqltag` | INT64 | Meaning not documented in the repo. |
| `cqlautono` | INT64 | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/cql.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.cql](/initial/raw_mac5_ag01/cql.md), [raw_mac5_aa05.cql](/initial/raw_mac5_aa05/cql.md), [raw_mac5_ab01.cql](/initial/raw_mac5_ab01/cql.md), [raw_mac5_ac02.cql](/initial/raw_mac5_ac02/cql.md), [raw_mac5_ak02.cql](/initial/raw_mac5_ak02/cql.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `cqlbank`, `cqlyear`, `cqlmonth`.
- Approximate size (BigQuery metadata, 2026-10-31): 316,924 rows, 36.7 MB.

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

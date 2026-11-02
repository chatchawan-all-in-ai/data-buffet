---
type: BigQuery Table
title: "fact_chq"
description: "One row = one cheque (chqno) per customer per company, linked to the receipt line (cqlvnos) that records it, for cheques with cqlbook = 0."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_chq&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_chq
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_chq.sqlx"
    title: "Dataform definition (fact/fact_chq.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Cheque register for accounts receivable: every customer cheque from MAC5 `chq`, with Thai/English status labels, linked to the receipt document (`cqlvnos`) from `cql`. It answers which cheques were received, their dates, amounts, bank and clearing status. It is the cheque side of the AR chain `fact_chq` -> [fact_mir_vs](/fact/fact_mir_vs.md) -> [fact_mir_rs](/fact/fact_mir_rs.md); `fact_mir_rs` FULL JOINs it on `cqlvnos = mirvnos`.

Used by / context: used by [fact_table.fact_mir_rs](/fact/fact_mir_rs.md).

# Grain and key

One row per `FactChqSK` (a `ROW_NUMBER()` over `company_id, chqno, cqlcus, cqlvnos`). Business grain is cheque number + customer + company + receipt document. Only cheque rows matching a `cql` row (`chqno = cqlno`, `chqcus = cqlcus`, `chqtotal = cqlsuml`, company) with `cqlbook = 0` survive (the WHERE on the left-joined `cql` turns it into an inner join).

# Schema

| Column | Type | Description |
|---|---|---|
| `FactChqSK` | INT64 | Surrogate key: ROW_NUMBER over company_id, chqno, cqlcus, cqlvnos. Regenerates daily. |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) via `chqcus = debcode` and company; NULL if unmatched. |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md) via `company_id`. |
| `company_id` | STRING | MAC5 company code. Pass-through of validated `chq.company_id`. |
| `chqno` | STRING | Cheque number. |
| `chqbank` | STRING | Bank code of the cheque (e.g. `BBL`, `KBANK`, `SCB`). |
| `chqacode` | STRING | General-ledger account code of the cheque; sampled MAC5 records show 112001 for received cheques and 211101, 212000, 212400, and 214201 for issued cheques. |
| `chqcus` | STRING | Customer code (supplier code for issued cheques), matching `deb.debcode`. |
| `chqdatec` | DATETIME | Date written on the cheque. |
| `chqdater` | DATETIME | Date the cheque was received or issued. |
| `chqdatep` | DATETIME | Date the cheque was passed (cleared) at the bank. |
| `chqtype` | INT64 | Cheque direction (1 = received from customer, 2 = issued to supplier). |
| `chqstatus` | STRING | Status label derived from `chq.chqstatus`: 1 'Cleared', 2 'Bounced', 3 'Due', otherwise NULL. |
| `chqstatusn` | STRING | Detailed status label derived from `chq.chqstatusn`: 1 'POST', 2 'PASS', 3 cleared (Thai), 4 not yet cleared (Thai), 5 adjusted (Thai), 6 voucher cancelled (Thai), otherwise NULL. |
| `chqtotal` | FLOAT64 | Cheque amount. |
| `chqmemo` | STRING | Cheque memo prefix before the transfer or payment-split notes. |
| `chqgl` | INT64 | Flag: cheque posted to the general ledger (1 = posted). |
| `cqlvnos` | STRING | Number of the receipt or payment document the cheque settles (e.g. `RI-...`). |

# How it is built

- Definition: `definitions/fact/fact_chq.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactChqSK`.
- Storage options: `{"clusterBy": ["FactChqSK"]}`.
- Reads: [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`), runs after `dim_customer` and `dim_company` (dependencies[]). Runs before `fact_mir_rs`. `FactChqSK` regenerates every run.
- Approximate size (BigQuery metadata, 2026-10-31): 135,394 rows, 18.8 MB.

# Examples

Cheques by status for one company.
```sql
SELECT chqstatus, COUNT(*) AS cheques, SUM(chqtotal) AS total
FROM `databuffet-nonprd.fact_table.fact_chq`
WHERE company_id = 'ag01'
GROUP BY chqstatus;
```
Cheques falling due in the next 30 days (Asia/Bangkok).
```sql
SELECT company_id, chqno, chqcus, chqdatep, chqtotal
FROM `databuffet-nonprd.fact_table.fact_chq`
WHERE DATE(chqdatep) BETWEEN CURRENT_DATE('Asia/Bangkok') AND DATE_ADD(CURRENT_DATE('Asia/Bangkok'), INTERVAL 30 DAY);
```

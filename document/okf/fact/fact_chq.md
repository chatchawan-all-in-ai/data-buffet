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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Cheque register for accounts receivable: every cheque (received, `chqtype` 1, and issued, `chqtype` 2) from MAC5 `chq` with a `cql` row where `cqlbook = 0`, with Thai/English status labels, linked to the receipt document (`cqlvnos`) from `cql`. It answers which cheques were received, their dates, amounts, bank and clearing status. It is the cheque side of the AR chain `fact_chq` -> [fact_mir_vs](/fact/fact_mir_vs.md) -> [fact_mir_rs](/fact/fact_mir_rs.md); `fact_mir_rs` FULL JOINs it on `cqlvnos = mirvnos`.

Read by: [fact_mir_rs](/fact/fact_mir_rs.md).

# Grain and key

One row = one cheque (`chqno`) of one customer on one receipt document (`cqlvnos`) per company: key `FactChqSK` (see [Schema](#schema) for key generation). Only cheque rows matching a `cql` row (`chqno = cqlno`, `chqcus = cqlcus`, `chqtotal = cqlsuml`, company) with `cqlbook = 0` appear; the WHERE on the left-joined `cql` makes it an inner join.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactChqSK` | INT64 | Stable row key: FARM_FINGERPRINT of the typed company/cheque/customer/receipt grain plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) via `chqcus = debcode` and company; NULL if unmatched. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `company_id` | STRING | MAC5 company code. Pass-through of validated `chq.company_id`. |
| `chqno` | STRING | Cheque number. |
| `chqbank` | STRING | Bank code of the cheque (e.g. `BBL`, `KBANK`, `SCB`). |
| `chqacode` | STRING | General-ledger account code of the cheque. |
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
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`), runs after `dim_customer` and `dim_company` (dependencies[]). Runs before `fact_mir_rs`.

# Examples

Cheques by status for one company.
```sql
SELECT chqstatus, COUNT(*) AS cheques, SUM(chqtotal) AS total
FROM `databuffet-nonprd.fact_table.fact_chq`
WHERE company_id = 'ag01'
GROUP BY chqstatus;
```
Cheques dated (`chqdatec`) in the next 30 days (Asia/Bangkok).
```sql
SELECT company_id, chqno, chqcus, chqdatec, chqtotal
FROM `databuffet-nonprd.fact_table.fact_chq`
WHERE DATE(chqdatec) BETWEEN CURRENT_DATE('Asia/Bangkok') AND DATE_ADD(CURRENT_DATE('Asia/Bangkok'), INTERVAL 30 DAY);
```

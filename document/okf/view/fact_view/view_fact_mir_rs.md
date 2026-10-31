---
type: BigQuery View
title: "view_fact_mir_rs"
description: "One row = one receipt (mirtype RS) line or cheque of fact_mir_rs, extended with AgingSK and the receipt document's cancel flag and status name; ReceiveSK is unique."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_mir_rs&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_mir_rs
tags: ["view", "fact_view", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_mir_rs.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_mir_rs.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The BI-facing version of the `fact_mir_rs` receipt/payment-received fact. It adds the link to the AR aging dimension (`AgingSK`) and the status of the receipt document (`mihcancel`, `mihstatus`, Thai status text `ar_snamet`) to every `fact_mir_rs` column.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per `ReceiveSK` (the key of [fact_mir_rs](/fact/fact_mir_rs.md)). `dim_aging` can hold several rows per invoice number, so the view ends with `QUALIFY ROW_NUMBER() OVER (PARTITION BY t1.ReceiveSK ORDER BY t2.AgingSK DESC) = 1`; this makes the row count equal to `fact_mir_rs`. This removes extra aging matches per ReceiveSK, but preserves the fact's cheque expansion: one validated receipt line can still occur under several ReceiveSK values.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingSK` | INT64 | SK of `dim_aging` for the invoice paid (join `mirbinvno = cfsvnosid`, `company_id = companyID`); highest AgingSK kept when several rows match. NULL when the invoice has no aging row or on cheque-only rows. Regenerated daily. |
| `ReceiveSK` | INT64 | Row key of `fact_mir_rs` = `ROW_NUMBER()` over (BillingSK, FactChqSK, company_id, mirtype, mirvnos, mirlistno, mirbinvno). Unique in this view. Regenerated daily. |
| `BillingSK` | INT64 | SK of the matching billing row in `fact_mir_vs` (match company + `mirbinvno`); NULL when the paid invoice was never billed. Regenerated daily. |
| `FactChqSK` | INT64 | SK of the matching cheque row in `fact_chq` (match `cqlvnos = mirvnos`, customer, company). `fact_mir_rs` uses a FULL JOIN with `fact_chq`, so cheque rows without a receipt line also appear (the receipt-side columns are then NULL). Regenerated daily. |
| `CollectSK` | INT64 | SK of `dim_collection_status`, matched on company + year + month + customer of the document; NULL when no collection-status row exists. Regenerated daily like all full-rebuild dim SKs. |
| `Actions` | STRING | Collection action text from `dim_collection_status` (matched as for CollectSK). |
| `Justification` | STRING | Collection justification text from `dim_collection_status`. |
| `Responsible` | STRING | Person/role responsible for collection, from `dim_collection_status`. |
| `CustomerSK` | INT64 | SK of `dim_customer` (match `mircus` = `debcode` + company). `dim_customer` is a MERGE dim with stable SKs. |
| `InvoiceSK` | INT64 | SK of `dim_invoice` (match on invoice number, type, customer, date and company, first SK kept). `dim_invoice` is a MERGE dim with stable SKs. |
| `CompanySK` | INT64 | SK of `dim_company` (match `company_id`); stable across days. |
| `duedate` | DATE | Due date of the billed invoice: `PARSE_DATE('%d/%m/%Y', SUBSTR(mie.miectermdx, 1, 10))` from validated `mie`, joined on invoice number + customer + company. NULL when no `mie` row matches. |
| `company_id` | STRING | Company code (ag01/aa05/ab01/ac02/ak02), pass-through of `validated_mac5.mir.company_id`. Joins to `dim_company.companyID`. |
| `mirday` | INT64 | Day of month of the receipt/billing document date (`validated_mac5.mir.mirday`). Combine with `miryear`/`mirmonth` to get the date. |
| `mirmonth` | INT64 | Month of the document date (`validated_mac5.mir.mirmonth`). |
| `miryear` | INT64 | Year of the document date (`validated_mac5.mir.miryear`). |
| `mirtype` | STRING | Document type of the `mir` row; `'RS'` (receipt/payment received) for receipt lines. Can be NULL on cheque-only rows produced by the FULL JOIN with `fact_chq`. |
| `mirvnos` | STRING | Document number of the MAC5 `mir` document itself (voucher number); pass-through of `validated_mac5.mir.mirvnos`. Joins to `curated_mih.mihvnos` with `mirtype`. |
| `mircus` | STRING | Customer code on the document (`validated_mac5.mir.mircus`); matches `dim_customer.debcode`. |
| `mirlistno` | INT64 | Line number within the `mir` document (`validated_mac5.mir.mirlistno`). |
| `mirbinvno` | STRING | Number of the invoice (`mih` document) that this line pays or bills; matches `cfsVnosID` in `dim_aging` and `mihVnos` in `dim_invoice`. |
| `mirbinvdate` | DATETIME | Date of that invoice (`validated_mac5.mir.mirbinvdate`, DATETIME). |
| `mirbinvtype` | STRING | Document type of that invoice (`validated_mac5.mir.mirbinvtype`), e.g. IS/BS/AS. |
| `mirdesc` | STRING | Free-text line description from MAC5 (`validated_mac5.mir.mirdesc`). |
| `mircog` | FLOAT64 | Pass-through of `validated_mac5.mir.mircog` (FLOAT64). Meaning not documented in the repo (likely a cost/gross amount, inferred from the name). |
| `mirvat` | FLOAT64 | VAT amount of the line, pass-through of `validated_mac5.mir.mirvat` (inferred from the name). |
| `mirsum` | FLOAT64 | Receipt-line amount from `validated_mac5.mir.mirsum`, repeated for each matched cheque. |
| `mircurc` | INT64 | Currency code of the line (`validated_mac5.mir.mircurc`); meaning of the codes not documented in the repo. |
| `mirexchg` | FLOAT64 | Exchange rate of the line (`validated_mac5.mir.mirexchg`). |
| `mirtag` | INT64 | Pass-through of `validated_mac5.mir.mirtag`. Meaning not documented in the repo. |
| `mirnotes` | STRING | Free-text notes on the line (`validated_mac5.mir.mirnotes`). |
| `miraccount` | STRING | Account code on the line (`validated_mac5.mir.miraccount`); meaning not further documented in the repo. |
| `asatdate` | DATE | Load date (ASATDATE partition value) of the source `validated_mac5.mir` row; not a business date. |
| `mihcancel` | INT64 | Cancel flag of the receipt document, from `curated_mih` (join `mirvnos = mihvnos`, `mirtype = mihtype`, company). `fact_mir_rs` only keeps `mihcancel = 0`, so it is normally 0 (NULL on cheque-only rows). |
| `mihstatus` | INT64 | Status code of the receipt document from `curated_mih` (`mihstatus`); joins to `validated_mac5.ar_s.ar_scode` per company. |
| `ar_snamet` | STRING | Thai status name for `mihstatus` from `validated_mac5.ar_s.ar_snamet` (join `mihstatus = ar_scode`, company). |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_mir_rs.sqlx` (`type: "view"`, tags `view`).
- Reads: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [fact_table.fact_mir_rs](/fact/fact_mir_rs.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; `fact_mir_rs` and `dim_aging` are rebuilt first (declared in `dependencies`); `curated_mih` and `validated_mac5.ar_s` are read via `ref()`.

# Examples

Receipts per company and month for non-cancelled documents.

```sql
WITH receipt_lines AS (
  SELECT company_id, miryear, mirmonth, mirsum,
         ROW_NUMBER() OVER (
           PARTITION BY company_id, mirtype, mirvnos, mirlistno
           ORDER BY ReceiveSK
         ) AS receipt_row
  FROM `databuffet-nonprd.fact_view.view_fact_mir_rs`
  WHERE mirtype = 'RS' AND mihcancel = 0
)
SELECT company_id, miryear, mirmonth, SUM(mirsum) AS received_amount
FROM receipt_lines
WHERE receipt_row = 1
GROUP BY company_id, miryear, mirmonth
ORDER BY company_id, miryear, mirmonth
```

Receipt amount by Thai status name of the receipt document.

```sql
WITH receipt_lines AS (
  SELECT ar_snamet, mirsum,
         ROW_NUMBER() OVER (
           PARTITION BY company_id, mirtype, mirvnos, mirlistno
           ORDER BY ReceiveSK
         ) AS receipt_row
  FROM `databuffet-nonprd.fact_view.view_fact_mir_rs`
  WHERE mirtype = 'RS'
)
SELECT ar_snamet, COUNT(*) AS lines, SUM(mirsum) AS received_amount
FROM receipt_lines
WHERE receipt_row = 1
GROUP BY ar_snamet
ORDER BY received_amount DESC
```

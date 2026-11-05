---
type: BigQuery View
title: "view_fact_mir_rs"
description: "One row = one receipt (mirtype RS) line or cheque of fact_mir_rs, extended with AgingSK and the receipt document's cancel flag and status name; ReceiveSK is unique."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_mir_rs&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_mir_rs
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_mir_rs.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_mir_rs.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The view over the `fact_mir_rs` receipt/payment-received fact. It adds the link to the AR aging dimension (`AgingSK`) and the status of the receipt document (`mihcancel`, `mihstatus`, Thai status text `ar_snamet`) to every `fact_mir_rs` column.

No other repo object reads it.

# Grain and key

One row = one receipt (RS) line or cheque of [fact_mir_rs](/fact/fact_mir_rs.md): key `ReceiveSK` (unique). The view joins `dim_aging` on invoice number and company, which can match several rows per invoice number (different `cfsTypeID`), so it ends with `QUALIFY ROW_NUMBER() OVER (PARTITION BY t1.ReceiveSK ORDER BY t2.AgingSK DESC) = 1`; this makes the row count equal to `fact_mir_rs`. This removes extra aging matches per ReceiveSK, but preserves the fact's cheque expansion: one validated receipt line can still occur under several ReceiveSK values.

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
| `company_id` | STRING | MAC5 company code, pass-through of `validated_mac5.mir.company_id`. Joins to `dim_company.companyID`. |
| `mirday` | INT64 | Day part of the document date. |
| `mirmonth` | INT64 | Month part of the document date. |
| `miryear` | INT64 | Year part of the document date (Gregorian). |
| `mirtype` | STRING | Document type code (`RS` = sales receipt; NULL on cheque-only rows). |
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
| `asatdate` | DATE | Load date (ASATDATE partition value) of the source `validated_mac5.mir` row; not a business date. |
| `mihcancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihstatus` | INT64 | Document status code; meaning in `ar_s` for sales types and `ap_s` for purchase types (e.g. 26 = approved sales order, 30 = VAT sale, 32 = cancelled tax invoice). |
| `ar_snamet` | STRING | Thai status name for `mihstatus` from `validated_mac5.ar_s.ar_snamet` (join `mihstatus = ar_scode`, company). |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_mir_rs.sqlx` (`type: "view"`, tags `view`).
- Reads: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [fact_table.fact_mir_rs](/fact/fact_mir_rs.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md).

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

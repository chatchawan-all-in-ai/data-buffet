---
type: BigQuery Table
title: "fact_mir_vs"
description: "One row = one billing (VS) document line of a company that bills an invoice (mirbinvno), de-duplicated to one row per invoice."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_mir_vs&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_mir_vs
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_mir_vs.sqlx"
    title: "Dataform definition (fact/fact_mir_vs.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Billing-note (VS, billing/collection document) fact for accounts receivable aging: which invoices were put on a billing note, with the customer, invoice SK, collection-status SK and invoice due date. It answers which invoices are billed and when they fall due. It feeds [dim_aging](/dimension/dim_aging.md) (which declares it as a dependency), [dim_aging_history](/dimension/dim_aging_history.md), `view_aging_ri`, `view_fact_mir_vs` and [fact_mir_rs](/fact/fact_mir_rs.md) (BillingSK).

Used by / context: used by [fact_table.fact_mir_rs](/fact/fact_mir_rs.md), [dimension_view.view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [fact_view.view_fact_mir_vs](/view/fact_view/view_fact_mir_vs.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md).

# Grain and key

One row per `BillingSK` (ROW_NUMBER over company_id, mirtype, mirvnos, mirlistno, mirbinvno). Source `mir` is restricted to `mirtype = 'VS'` and de-duplicated with `QUALIFY ROW_NUMBER() OVER(PARTITION BY mir.mirbinvno ORDER BY miryear DESC, mirmonth DESC, mirday DESC) = 1`, so each invoice number (`mirbinvno`) appears once, on its latest billing document. The partition ignores `company_id`.

# Schema

| Column | Type | Description |
|---|---|---|
| `BillingSK` | INT64 | Surrogate key: ROW_NUMBER over company_id, mirtype, mirvnos, mirlistno, mirbinvno. Regenerates daily; `fact_mir_rs.BillingSK` points to it. |
| `CollectSK` | INT64 | Surrogate key of [dim_collection_status](/dimension/dim_collection_status.md), joined on company, receipt year/month and customer (`mircus` cast to STRING = `CustomerID`). NULL when the MDS collection-status master has no row for that month/customer. Regenerates daily. |
| `Actions` | STRING | Collection action text, copied from `dim_collection_status.Actions` (MDS collection-status master). |
| `Justification` | STRING | Collection justification text, copied from `dim_collection_status.Justification`. |
| `Responsible` | STRING | Person/role responsible for the collection follow-up, copied from `dim_collection_status.Responsible`. |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md), joined on `mircus = debcode` and `company_id = companyID`. NULL when the customer is not in the dimension. |
| `InvoiceSK` | INT64 | Surrogate key of [dim_invoice](/dimension/dim_invoice.md) for the invoice this line settles (`mirbinvno`, `mirbinvtype`, `mircus`, `mirbinvdate = mix_date`, company); dim_invoice is first de-duplicated to one row per that key. |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md), joined on `company_id = companyID`. |
| `duedate` | DATE | Invoice due date: first 10 characters of `mie.miectermdx` parsed as `dd/mm/yyyy`, where mie is the validated MAC5 invoice-extension row matched on `mirbinvno = mievnos`, `mircus = miecus`, company. NULL when no mie match. |
| `company_id` | STRING | MAC5 company code (ag01, aa05, ab01, ac02, ak02). Pass-through of validated `mir.company_id`. |
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
| `asatdate` | DATE | Snapshot/extract date carried from validated `mir.asatdate` (DATE). |

# How it is built

- Definition: `definitions/fact/fact_mir_vs.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `BillingSK`.
- Storage options: `{"clusterBy": ["BillingSK", "InvoiceSK", "CustomerSK"]}`.
- Reads: [dimension_table.dim_invoice](/dimension/dim_invoice.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_collection_status](/dimension/dim_collection_status.md), [validated_mac5.mie](/validated/validated_mac5/mie.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `BillingSK`), after `dim_invoice`, `dim_customer`, `dim_collection_status`, `dim_company` and before `fact_mir_rs` and `dim_aging`. `BillingSK` regenerates daily.

# Examples

Billed invoices due within 14 days for one company.
```sql
SELECT company_id, mirbinvno, mircus, mirsum, duedate
FROM `databuffet-nonprd.fact_table.fact_mir_vs`
WHERE company_id = 'ag01'
  AND duedate BETWEEN CURRENT_DATE('Asia/Bangkok') AND DATE_ADD(CURRENT_DATE('Asia/Bangkok'), INTERVAL 14 DAY);
```
Billed amount per customer and month of the billing document.
```sql
SELECT CustomerSK, miryear, mirmonth, SUM(mirsum) AS billed
FROM `databuffet-nonprd.fact_table.fact_mir_vs`
GROUP BY CustomerSK, miryear, mirmonth;
```

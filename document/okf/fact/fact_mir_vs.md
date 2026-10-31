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
| `duedate` | DATE | Invoice due date: first 10 characters of `mie.miectermdx` parsed as `dd/mm/yyyy`, where mie is the validated MAC5 invoice-extension row matched on `mirbinvno = mievnos`, `mircus = miecus`, company. (Meaning of `miectermdx` inferred from usage.) NULL when no mie match. |
| `company_id` | STRING | MAC5 company code (ag01, aa05, ab01, ac02, ak02). Pass-through of validated `mir.company_id`. |
| `mirday` | INT64 | Day part of the receipt/billing document date. Pass-through of validated `mir.mirday` (meaning inferred from the name). |
| `mirmonth` | INT64 | Month part of the receipt/billing document date. Pass-through of validated `mir.mirmonth`; used with `miryear` to join dim_collection_status. |
| `miryear` | INT64 | Year part of the receipt/billing document date. Pass-through of validated `mir.miryear`; used with `mirmonth` to join dim_collection_status. |
| `mirtype` | STRING | Document type of the mir row. Always 'VS' in this table (filter `mirtype = 'VS'`). |
| `mirvnos` | STRING | Document number (vnos) of the receipt/billing document. Pass-through of validated `mir.mirvnos`; with `mirtype` it joins to `curated_mih`. |
| `mircus` | STRING | Customer code (matches `dim_customer.debcode` and `deb`). Pass-through of validated `mir.mircus`. |
| `mirlistno` | INT64 | Line number within the document. Pass-through of validated `mir.mirlistno` (meaning inferred from the name). |
| `mirbinvno` | STRING | Number of the invoice this line is billed/received against (joins `dim_invoice.mihVnos`). Pass-through of validated `mir.mirbinvno`. |
| `mirbinvdate` | DATETIME | Date of that invoice (joins `dim_invoice.mix_date`). Pass-through of validated `mir.mirbinvdate`. |
| `mirbinvtype` | STRING | Type of that invoice (joins `dim_invoice.mihType`). Pass-through of validated `mir.mirbinvtype`. |
| `mirdesc` | STRING | Line description. Pass-through of validated `mir.mirdesc` (meaning inferred from the name). |
| `mircog` | FLOAT64 | Pass-through of validated `mir.mircog`. Meaning not documented in the repo (likely a cost/goods-related amount, inferred from the name). |
| `mirvat` | FLOAT64 | VAT amount of the line. Pass-through of validated `mir.mirvat` (meaning inferred from the name). |
| `mirsum` | FLOAT64 | Line amount. Pass-through of validated `mir.mirsum`; the monetary measure of the document (THB). |
| `mircurc` | INT64 | Currency code. Pass-through of validated `mir.mircurc` (meaning inferred from the name). |
| `mirexchg` | FLOAT64 | Exchange rate. Pass-through of validated `mir.mirexchg` (meaning inferred from the name). |
| `mirtag` | INT64 | Pass-through of validated `mir.mirtag`. Meaning not documented in the repo. |
| `mirnotes` | STRING | Free-text notes. Pass-through of validated `mir.mirnotes` (meaning inferred from the name). |
| `miraccount` | STRING | Account code. Pass-through of validated `mir.miraccount` (meaning inferred from the name). |
| `asatdate` | DATE | Snapshot/extract date carried from validated `mir.asatdate` (DATE). |

# How it is built

- Definition: `definitions/fact/fact_mir_vs.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `BillingSK`.
- Storage options: `{"clusterBy": ["BillingSK", "InvoiceSK", "CustomerSK"]}`.
- Reads: [dimension_table.dim_invoice](/dimension/dim_invoice.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_collection_status](/dimension/dim_collection_status.md), [validated_mac5.mie](/validated/validated_mac5/mie.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `BillingSK`), after `dim_invoice`, `dim_customer`, `dim_collection_status`, `dim_company` and before `fact_mir_rs` and `dim_aging`. `BillingSK` regenerates daily.
- Approximate size (BigQuery metadata, 2026-10-31): 1,263,383 rows, 733.8 MB.

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

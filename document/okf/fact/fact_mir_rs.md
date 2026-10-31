---
type: BigQuery Table
title: "fact_mir_rs"
description: "One row = one receipt (RS) document line against an invoice, optionally matched to the billing row (BillingSK) and to the cheque (FactChqSK) that paid it, or a cheque with no receipt line."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_mir_rs&page=table"
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_mir_rs.sqlx"
    title: "Dataform definition (fact/fact_mir_rs.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Receipt (RS, payment received) fact for the accounts-receivable chain: each receipt line with its invoice, customer and collection status, joined to the billing note in [fact_mir_vs](/fact/fact_mir_vs.md) and FULL JOINed to cheques in [fact_chq](/fact/fact_chq.md). It answers which invoices were paid, by which cheque, and which cheques have no receipt yet (and vice versa).

Used by / context: used by [fact_view.view_fact_mir_rs](/view/fact_view/view_fact_mir_rs.md).

# Grain and key

One row per `ReceiveSK` (ROW_NUMBER over BillingSK, FactChqSK, company_id, mirtype, mirvnos, mirlistno, mirbinvno). Base grain is an RS `mir` line (company_id, mirtype, mirvnos, mirlistno). The FULL JOIN to `fact_chq` on `cqlvnos = mirvnos` AND `chqcus = mircus` AND company AND `mirtype = 'RS'` can add rows where only the cheque side exists (all `mir*` columns NULL) and can multiply a receipt line when several cheques share the receipt number.

# Schema

| Column | Type | Description |
|---|---|---|
| `ReceiveSK` | INT64 | Surrogate key: ROW_NUMBER over BillingSK, FactChqSK, company_id, mirtype, mirvnos, mirlistno, mirbinvno. Regenerates daily. |
| `BillingSK` | INT64 | [fact_mir_vs](/fact/fact_mir_vs.md).BillingSK for the same company and `mirbinvno`; NULL when the invoice has no billing (VS) row. |
| `FactChqSK` | INT64 | [fact_chq](/fact/fact_chq.md).FactChqSK of the cheque matched on receipt number (`cqlvnos = mirvnos`), customer and company; NULL when no cheque matches. |
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
| `mirtype` | STRING | Document type of the mir row. 'RS' for receipt lines; NULL on cheque-only rows from the FULL JOIN. |
| `mirvnos` | STRING | Document number (vnos) of the receipt/billing document. Pass-through of validated `mir.mirvnos`; with `mirtype` it joins to `curated_mih`. |
| `mircus` | STRING | Customer code (matches `dim_customer.debcode` and `deb`). Pass-through of validated `mir.mircus`. |
| `mirlistno` | INT64 | Line number within the document. Pass-through of validated `mir.mirlistno` (meaning inferred from the name). |
| `mirbinvno` | STRING | Number of the invoice this line is billed/received against (joins `dim_invoice.mihVnos`). Pass-through of validated `mir.mirbinvno`. |
| `mirbinvdate` | DATETIME | Date of that invoice (joins `dim_invoice.mix_date`). Pass-through of validated `mir.mirbinvdate`. |
| `mirbinvtype` | STRING | Type of that invoice (joins `dim_invoice.mihType`). Pass-through of validated `mir.mirbinvtype`. |
| `mirdesc` | STRING | Line description. Pass-through of validated `mir.mirdesc` (meaning inferred from the name). |
| `mircog` | FLOAT64 | Pass-through of validated `mir.mircog`. Meaning not documented in the repo (likely a cost/goods-related amount, inferred from the name). |
| `mirvat` | FLOAT64 | VAT amount of the line. Pass-through of validated `mir.mirvat` (meaning inferred from the name). |
| `mirsum` | FLOAT64 | Receipt-line amount (THB), passed through from validated `mir.mirsum` and repeated on every matching cheque row. |
| `mircurc` | INT64 | Currency code. Pass-through of validated `mir.mircurc` (meaning inferred from the name). |
| `mirexchg` | FLOAT64 | Exchange rate. Pass-through of validated `mir.mirexchg` (meaning inferred from the name). |
| `mirtag` | INT64 | Pass-through of validated `mir.mirtag`. Meaning not documented in the repo. |
| `mirnotes` | STRING | Free-text notes. Pass-through of validated `mir.mirnotes` (meaning inferred from the name). |
| `miraccount` | STRING | Account code. Pass-through of validated `mir.miraccount` (meaning inferred from the name). |
| `asatdate` | DATE | Snapshot/extract date carried from validated `mir.asatdate` (DATE). |

# How it is built

- Definition: `definitions/fact/fact_mir_rs.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `ReceiveSK`.
- Storage options: `{"clusterBy": ["ReceiveSK", "FactChqSK", "InvoiceSK"]}`.
- Reads: [dimension_table.dim_invoice](/dimension/dim_invoice.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_collection_status](/dimension/dim_collection_status.md), [validated_mac5.mie](/validated/validated_mac5/mie.md), [dimension_table.dim_company](/dimension/dim_company.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [fact_table.fact_chq](/fact/fact_chq.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `ReceiveSK`), after `fact_mir_vs` and `fact_chq` plus the dims (dependencies[]). `ReceiveSK` regenerates daily.
- Approximate size (BigQuery metadata, 2026-10-31): 1,772,772 rows, 992.8 MB.

# Examples

Receipt-line totals per customer and month, counting each validated receipt line once.
```sql
WITH receipt_lines AS (
  SELECT CustomerSK, miryear, mirmonth, mirsum,
         ROW_NUMBER() OVER (
           PARTITION BY company_id, mirtype, mirvnos, mirlistno
           ORDER BY ReceiveSK
         ) AS receipt_row
  FROM `databuffet-nonprd.fact_table.fact_mir_rs`
  WHERE mirtype = 'RS'
)
SELECT CustomerSK, miryear, mirmonth, COUNT(*) AS lines, SUM(mirsum) AS received
FROM receipt_lines
WHERE receipt_row = 1
GROUP BY CustomerSK, miryear, mirmonth;
```
Cheques that have no receipt line yet.
```sql
SELECT FactChqSK
FROM `databuffet-nonprd.fact_table.fact_mir_rs`
WHERE FactChqSK IS NOT NULL AND mirvnos IS NULL;
```

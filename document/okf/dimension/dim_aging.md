---
type: BigQuery Table
title: "dim_aging"
description: "One row = one AR document (tax invoice IS, credit note BS or debit note AS) per company with its payment, credit/debit-note adjustments, outstanding balance, completion flag and invoice-group flag."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_aging&page=table"
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_aging.sqlx"
    title: "Dataform definition (dimension/dim_aging.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Accounts-receivable aging base table for MAC5. Each row is an invoice (IS) or credit/debit note (BS/AS) from `curated_mih`, enriched with customer and invoice SKs, due dates, how much has been received (`mir` receipts, cheque extraction via `chq`/`cql`), credit/debit-note adjustments and the resulting outstanding balance. It answers "who owes us what and since when". `flagComplete` / `GroupFlagComplete` say whether a document (or its whole linked invoice group) is settled. It is not queried directly by BI: [view_dim_aging](/view/dimension_view/view_dim_aging.md) adds channel, `DayRange` and `AgingRangSK`, and the daily snapshot of non-completed rows is stored in [dim_aging_history](/dimension/dim_aging_history.md).

Used by: [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md), [dimension_view.view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [fact_view.view_fact_mir_rs](/view/fact_view/view_fact_mir_rs.md), [fact_view.view_fact_mir_vs](/view/fact_view/view_fact_mir_vs.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md).

# Grain and key

One row per (`companyID`, `cfsVnosID`, `cfsTypeID`) document, i.e. one invoice/credit note/debit note. `AgingSK` is the surrogate key but is a plain `ROW_NUMBER()` regenerated on every run, so it is not stable. The key pair is not enforced as unique; the history view de-duplicates on the natural key. Cancelled documents (`mihcancel <> 0`), documents dated in the future, documents in `onetime.cfsinvclose2024` for ag01, and BS/AS statuses named as deposit/cancel in `ar_s` are excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingSK` | INT64 | Surrogate key, `ROW_NUMBER() OVER(ORDER BY CompanySK, InvoiceNo, InvoiceDate)` over the whole table. Regenerated every run. |
| `BillingSK` | INT64 | Surrogate key of the billing (receipt) fact row, joined from [fact_mir_vs](/fact/fact_mir_vs.md) on `InvoiceNo = mirbinvno` and company. NULL when the invoice has no billing row. Regenerated daily upstream. |
| `CustomerSK` | INT64 | Customer surrogate key from [dim_customer](/dimension/dim_customer.md), joined on `debcode` (the invoice's `mihCus`) and `CompanySK`. NULL when no customer matches. |
| `InvoiceSK` | INT64 | Invoice surrogate key from [dim_invoice](/dimension/dim_invoice.md), joined on document number (`mihVnos`) and `CompanySK` (first SK per company and document number). |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), joined on company id. |
| `companyID` | STRING | MAC5 company code (ag01 / aa05 / ab01 / ac02 / ak02), from `dim_company.companyID`. |
| `dueDate` | DATE | Due date of the document: the date parsed from MAC5 `mie.MIEctermDX` (dd/mm/yyyy text) when present, otherwise `invoiceDate + transCreditTerm` days. |
| `realDueDate` | DATE | Computed due date, always `invoiceDate + transCreditTerm` days (ignores the MIE override used in `dueDate`). |
| `invoiceDate` | DATE | Document date, built from `mihYear/mihMonth/mihDay` of [curated_mih](/curated/curated_mac5/curated_mih.md). |
| `cfsVnosID` | STRING | Document number (`mihVnos`) of the invoice or note. Natural key together with `companyID` and `cfsTypeID`. |
| `cfsTypeID` | STRING | Document type (`mihType`): IS = tax invoice, BS = credit note, AS = debit note. |
| `cfsJob` | STRING | Job code `mihJob` of the document header (pass-through). |
| `cfsDep` | STRING | Department code `mihDep` of the document header; joins to channel/department by `DepCode` in the views. |
| `cfsPer` | STRING | Salesperson/employee code `mihPer` of the document header (pass-through). |
| `debCode` | STRING | Customer (debtor) code, `mihCus` of the document. |
| `debName` | STRING | Customer Thai name from `dim_customer.debnamet`. |
| `calCreditTerm` | INT64 | Credit term in days used for the aging calculation (= `transCreditTerm`, i.e. `mihstanding`). |
| `debCreditTerm` | INT64 | Credit term in days on the customer master (`dim_customer.DEBcreditTerm`), for comparison with the term on the document. |
| `transCreditTerm` | INT64 | Credit term in days recorded on the document itself (`mihstanding`; MAX over grouped rows for notes). |
| `debLimit` | FLOAT64 | Customer credit limit from `dim_customer.debLimit`. |
| `debMemo` | STRING | Customer memo text from `dim_customer.debMemo`. |
| `channel` | STRING | Always NULL (placeholder `CAST(NULL AS STRING)`); channel is attached later in the views via `dim_channel`. |
| `mihRef2` | STRING | Always NULL (placeholder). |
| `mihNote` | STRING | Document notes `mihNotes` from the header. |
| `mihRef1` | STRING | Linked invoice reference. For IS rows: pipe-separated (`/`) list of the credit/debit note numbers that point at this invoice. For BS/AS rows: pipe-separated list of invoice numbers they reference (`milLinkVcno`, blanked when the invoice is in `onetime.cfsinvclose2024`). |
| `TotalAmount` | FLOAT64 | Document net total (`mihNetSum`), rounded to 2 decimals for notes. |
| `PaymentAmount` | FLOAT64 | Amount received against the document: sum of RS receipt amounts from `mir` (with the cheque-extract adjustment). If the document is flagged complete via `dim_status_not_receive` (year <= 2023) it equals TotalAmount. For BS/AS rows it is TotalAmount when any receipt exists, else 0. |
| `CreditNoteAmount` | FLOAT64 | Credit notes (type BS) attached to the invoice, `milSum * 1.07` summed (counts only notes with no receipt of their own). 0 on BS/AS rows. |
| `DebitNoteAmount` | FLOAT64 | Debit notes (type AS) attached to the invoice, `milSum * 1.07` summed (counts only notes with no receipt of their own). 0 on BS/AS rows. |
| `OutStanding` | FLOAT64 | Remaining balance: `TotalAmount - PaymentAmount + CreditNoteAmount + DebitNoteAmount`, rounded to 2 decimals; 0 when the status-complete rule applies. |
| `flagComplete` | STRING | 'Completed' when `OutStanding` is between -1 and 1, else 'Non-Completed'. For invoices dated before 2023 that are still non-complete, a legacy check on `cfs` (`cfsclearsum = -1` and `cfsclearall = -1`) can flip it to 'Completed'. |
| `MinReceiveDate` | DATE | Earliest receipt date for the document (from RS `mir` rows, or the cheque `extract_date` when cheque extraction applies). |
| `MaxReceiveDate` | DATE | Latest receipt date for the document (same sources as `MinReceiveDate`). |
| `GroupID` | STRING | Id of the invoice group: the smallest document number connected through invoice <-> credit/debit-note links (graph closure computed with hop_2 / hop_4 / hop_8 joins, so up to 8 hops). Scoped per company. |
| `GroupFlagComplete` | STRING | 'Completed' only if every document in the same (`CompanyID`, `GroupID`) is 'Completed', else 'Non-Completed'. |

# How it is built

- Definition: `definitions/dimension/dim_aging.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_status_not_receive](/dimension/dim_status_not_receive.md), [validated_mac5.mie](/validated/validated_mac5/mie.md), `onetime.cfsinvclose2024`, [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [validated_mac5.cfs](/validated/validated_mac5/cfs.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md).
- Refresh: full daily rebuild with `CREATE OR REPLACE TABLE ... CLUSTER BY AgingSK` inside a `type: "operations"` file, tag `dimension_daily`. Runs after `dim_company`, `dim_customer`, `dim_invoice`, `dim_status_not_receive` and `fact_mir_vs` (declared in `dependencies[]`). The same file then appends the daily snapshot to [dim_aging_history](/dimension/dim_aging_history.md) (reading [view_dim_aging](/view/dimension_view/view_dim_aging.md)).
- Approximate size (BigQuery metadata, 2026-10-31): 1,615,767 rows, 1.0 GB.

# Examples

Open (non-completed) AR per company as of the latest run.

```sql
SELECT companyID, COUNT(*) AS docs, ROUND(SUM(OutStanding), 2) AS outstanding
FROM `databuffet-nonprd.dimension_table.dim_aging`
WHERE GroupFlagComplete = 'Non-Completed' AND cfsTypeID = 'IS'
GROUP BY companyID
ORDER BY outstanding DESC;
```

Overdue invoices (due date passed, not completed) with their customer SK.

```sql
SELECT companyID, cfsVnosID, CustomerSK, dueDate, OutStanding
FROM `databuffet-nonprd.dimension_table.dim_aging`
WHERE flagComplete = 'Non-Completed'
  AND dueDate < CURRENT_DATE('Asia/Bangkok')
ORDER BY dueDate
LIMIT 100;
```

---
type: BigQuery Table
title: "dim_aging"
description: "One row = one AR document (tax invoice IS, credit note BS or debit note AS) per company with its payment, credit/debit-note adjustments, outstanding balance, completion flag and invoice-group flag."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_aging&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_aging
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_aging.sqlx"
    title: "Dataform definition (dimension/dim_aging.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Accounts-receivable aging base table for MAC5. Each row is an invoice (IS) or credit/debit note (BS/AS) from `curated_mih`, enriched with customer and invoice SKs, due dates, how much has been received (`mir` receipts, cheque extraction via `chq`/`cql`), credit/debit-note adjustments and the resulting outstanding balance. It answers "who owes us what and since when". `flagComplete` / `GroupFlagComplete` say whether a document (or its whole linked invoice group) is settled. [view_dim_aging](/view/dimension_view/view_dim_aging.md) adds channel, `DayRange` and `AgingRangSK`; the daily snapshot of non-completed rows is stored in [dim_aging_history](/dimension/dim_aging_history.md).

Read by: [view_dim_aging](/view/dimension_view/view_dim_aging.md), [view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md), [view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [view_fact_mir_rs](/view/fact_view/view_fact_mir_rs.md), [view_fact_mir_vs](/view/fact_view/view_fact_mir_vs.md).

# Grain and key

One row = one AR document (invoice, credit note or debit note): key (`companyID`, `cfsVnosID`, `cfsTypeID`), not enforced as unique. `AgingSK` is the surrogate key, a plain `ROW_NUMBER()` regenerated every run. Excluded: documents dated in the future; documents in `onetime.cfsinvclose2024` for ag01; IS rows with `mihcancel <> 0`; BS/AS rows whose status is named as deposit or cancellation in `ar_s`.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY CompanySK, InvoiceNo, InvoiceDate)` over the whole table. Regenerated every run. |
| `BillingSK` | INT64 | Row key of the billing-document row in [fact_mir_vs](/fact/fact_mir_vs.md#grain-and-key), joined on `InvoiceNo = mirbinvno` and company; NULL when the invoice has no billing row. |
| `CustomerSK` | INT64 | Customer surrogate key from [dim_customer](/dimension/dim_customer.md), joined on `debcode` (the invoice's `mihCus`) and `CompanySK`. NULL when no customer matches. |
| `InvoiceSK` | INT64 | Invoice surrogate key from [dim_invoice](/dimension/dim_invoice.md), joined on document number (`mihVnos`) and `CompanySK` (selected per company and document number by `mix_date DESC, mihType, mihCus, mihRef1, mihRef2, mihDesc`). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code (ag01 / aa05 / ab01 / ac02 / ak02), from `dim_company.companyID`. |
| `dueDate` | DATE | Due date of the document: the date parsed from MAC5 `mie.MIEctermDX` (dd/mm/yyyy text) when present, otherwise `invoiceDate + transCreditTerm` days. |
| `realDueDate` | DATE | Computed due date, always `invoiceDate + transCreditTerm` days (ignores the MIE override used in `dueDate`). |
| `invoiceDate` | DATE | Document date, built from `mihYear/mihMonth/mihDay` of [curated_mih](/curated/curated_mac5/curated_mih.md). |
| `cfsVnosID` | STRING | Document number (`mihVnos`) of the invoice or note. Natural key together with `companyID` and `cfsTypeID`. |
| `cfsTypeID` | STRING | Document type (`mihType`): IS = tax invoice, BS = credit note, AS = debit note. |
| `cfsJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `cfsDep` | STRING | Department code of the document, used as the sales channel code. |
| `cfsPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `debCode` | STRING | Customer (debtor) code. |
| `debName` | STRING | Customer name in Thai, from `dim_customer.debnamet`. |
| `calCreditTerm` | INT64 | Credit term in days used for the aging calculation (= `transCreditTerm`, i.e. `mihstanding`). |
| `debCreditTerm` | INT64 | Credit term in days, from `dim_customer.DEBcreditTerm`. |
| `transCreditTerm` | INT64 | Credit term in days recorded on the document (`mihstanding`; MAX over grouped rows for notes); `realDueDate` = `invoiceDate` + this value. |
| `debLimit` | FLOAT64 | Credit limit of the customer in baht, from `dim_customer.debLimit`. |
| `debMemo` | STRING | Free-text memo on the customer, from `dim_customer.debMemo`. |
| `channel` | STRING | Always NULL (placeholder `CAST(NULL AS STRING)`); channel is attached later in the views via `dim_channel`. |
| `mihRef2` | STRING | Always NULL as an aging-schema placeholder. |
| `mihNote` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihRef1` | STRING | Distinct linked document numbers separated by pipes: credit/debit notes for IS rows and referenced invoices for BS/AS rows, with links in the closed-invoice exclusion list omitted. |
| `TotalAmount` | FLOAT64 | `mihNetSum` of the document, rounded to 2 decimals. |
| `PaymentAmount` | FLOAT64 | Amount received against the document: sum of RS receipt amounts from `mir` (with the cheque-extract adjustment). If the document is flagged complete via `dim_status_not_receive` (year <= 2023) it equals TotalAmount. For BS/AS rows it is TotalAmount when any receipt exists, else 0. |
| `CreditNoteAmount` | FLOAT64 | Credit notes (type BS) attached to the invoice, `milSum * 1.07` summed (counts only notes with no receipt of their own). 0 on BS/AS rows. |
| `DebitNoteAmount` | FLOAT64 | Debit notes (type AS) attached to the invoice, `milSum * 1.07` summed (counts only notes with no receipt of their own). 0 on BS/AS rows. |
| `OutStanding` | FLOAT64 | Remaining balance. IS rows: `TotalAmount - PaymentAmount + CreditNoteAmount + DebitNoteAmount`, rounded to 2 decimals; 0 when the status-complete rule applies. BS/AS rows: 0 when the status-complete rule applies or when a receipt exists; `TotalAmount` when the note has no linked invoice (`mihRef1` is NULL); otherwise `TotalAmount` minus the note's own credit-note (BS) or debit-note (AS) amount (`milSum * 1.07` of all its lines), rounded to 2 decimals. |
| `flagComplete` | STRING | 'Completed' when `OutStanding` is between -1 and 1, else 'Non-Completed'. For invoices dated before 2023 that are still non-complete, a legacy check on `cfs` (`cfsclearsum = -1` and `cfsclearall = -1`) can flip it to 'Completed'. |
| `MinReceiveDate` | DATE | Earliest receipt date for the document (from RS `mir` rows, or the cheque `extract_date` when cheque extraction applies). |
| `MaxReceiveDate` | DATE | Latest receipt date for the document (same sources as `MinReceiveDate`). |
| `GroupID` | STRING | Id of the invoice group: the smallest document number connected through invoice <-> credit/debit-note links (graph closure computed with hop_2 / hop_4 / hop_8 joins, so up to 8 hops). Scoped per company. |
| `GroupFlagComplete` | STRING | 'Completed' only if every document in the same (`CompanyID`, `GroupID`) is 'Completed', else 'Non-Completed'. |

# How it is built

- Definition: `definitions/dimension/dim_aging.sqlx` (`type: "operations"`, tag `dimension_daily`); the operation owns this table.
- Reads: [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_status_not_receive](/dimension/dim_status_not_receive.md), [validated_mac5.mie](/validated/validated_mac5/mie.md), `onetime.cfsinvclose2024`, [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [validated_mac5.cfs](/validated/validated_mac5/cfs.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md) (for the history snapshot).
- Full daily rebuild (`CREATE OR REPLACE TABLE ... CLUSTER BY AgingSK` in a `type: "operations"` file, tag `dimension_daily`); runs after dim_company, dim_customer, dim_invoice, dim_status_not_receive and fact_mir_vs (declared in `dependencies[]`). The same file then appends the daily snapshot to [dim_aging_history](/dimension/dim_aging_history.md).

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

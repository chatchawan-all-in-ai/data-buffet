---
type: BigQuery View
title: "view_aging_ri"
description: "One row = one not-yet-fully-collected invoice, credit note or debit note per company (AR aging) with due dates, outstanding amount, aging days and receipt history text."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_aging_ri&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_aging_ri
tags: ["view", "fact_view", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_aging_ri.sqlx"
    title: "Dataform definition (view/fact_view/view_aging_ri.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The AR (accounts receivable) aging report for open items. It starts from [view_dim_aging](/view/dimension_view/view_dim_aging.md) (the aging dimension plus channel, DayRange and receipt-age fields), keeps only documents whose whole invoice group is still `Non-Completed`, and adds the customer PO number, the aging-bucket report name, the billing description/notes and two readable text columns that list every receipt (RI = receive invoice) with its status and cheque result.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per aging document: (`companyID`, `cfsVnosID`, `cfsTypeID`), i.e. one invoice (IS), credit note (BS) or debit note (AS). It inherits the uniqueness of `view_dim_aging` (one row per `AgingSK`, which this view drops together with `AgingRangSK`, `BillingSK`, `CustomerSK`, `InvoiceSK`, `CompanySK` and the four channel SKs). Rows are restricted to `GroupFlagComplete = 'Non-Completed'`. The extra joins (agg_mir, dim_aging_rang, dim_invoice, fact_mir_vs) are intended to be 1:1.

# Schema

| Column | Type | Description |
|---|---|---|
| `companyID` | STRING | Company code (ag01/aa05/ab01/ac02/ak02) from `dim_company.companyID`. |
| `dueDate` | DATE | Due date used for aging: `COALESCE(mie due date, invoiceDate + transCreditTerm)`. The `mie` date is parsed from the text field `MIEctermDX` (dd/mm/yyyy variants); falls back to the credit-term due date when absent. |
| `realDueDate` | DATE | `invoiceDate + transCreditTerm` (days), i.e. the due date from the credit term on the document itself, ignoring any `mie` override. |
| `invoiceDate` | DATE | Document date of the invoice (type IS) or credit/debit note (BS/AS) built from `mihYear/mihMonth/mihDay`. |
| `cfsVnosID` | STRING | Document number (`mihVnos`) of the invoice or note; with `companyID` and `cfsTypeID` it identifies the row. Joins to `dim_invoice.mihVnos` and `fact_mir_vs.mirbinvno`. |
| `cfsTypeID` | STRING | Document type: `IS` = invoice, `BS` = credit note (feeds CreditNoteAmount), `AS` = debit note (feeds DebitNoteAmount). |
| `cfsJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `cfsDep` | STRING | Department code of the document, used as the sales channel code. |
| `cfsPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `debCode` | STRING | Customer (debtor) code. |
| `debName` | STRING | Customer Thai name from `dim_customer.debnamet`. |
| `calCreditTerm` | INT64 | Credit term in days used in the aging calculation; equals `transCreditTerm` (`mihstanding` of the document). |
| `debCreditTerm` | INT64 | Credit term in days. |
| `transCreditTerm` | INT64 | Credit term in days stored on the document itself (`mihstanding`). |
| `debLimit` | FLOAT64 | Credit limit of the customer in baht. |
| `debMemo` | STRING | Free-text memo on the customer. |
| `channel` | STRING | Always NULL (`dim_aging` writes `CAST(NULL AS STRING)`). |
| `mihRef2` | STRING | Always NULL as an aging-schema placeholder. |
| `mihNote` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihRef1` | STRING | Distinct linked document numbers separated by pipes: credit/debit notes for IS rows and referenced invoices for BS/AS rows, with links in the closed-invoice exclusion list omitted. |
| `TotalAmount` | FLOAT64 | Net amount of the document (`mihNetSum`, rounded to 2 decimals for notes). |
| `PaymentAmount` | FLOAT64 | Amount received against the document (`RiAmount`): sum of RS receipt lines (cheque-adjusted); equals TotalAmount for old documents flagged complete by status. |
| `CreditNoteAmount` | FLOAT64 | Credit-note (BS) amount linked to the invoice (`mil.milSum * 1.07`, so VAT-inclusive at a fixed 7%); a BS row carries its own amount. |
| `DebitNoteAmount` | FLOAT64 | Debit-note (AS) amount linked to the invoice (same `milSum * 1.07` rule). |
| `OutStanding` | FLOAT64 | Remaining receivable: `TotalAmount - PaymentAmount + CreditNoteAmount + DebitNoteAmount`, rounded to 2 decimals; 0 for documents completed by status. Positive = still to collect. |
| `flagComplete` | STRING | `Completed` when OutStanding is within -1..1, otherwise `Non-Completed`; pre-2023 invoices that look open are also marked Completed when MAC5 cfs shows `cfsclearsum = -1 AND cfsclearall = -1` and a receipt exists. In this view it is mostly `Non-Completed` because of the group filter. |
| `MinReceiveDate` | DATE | Earliest receipt (RS) date for the document (cheque extract date for bounced/edited cheques). |
| `MaxReceiveDate` | DATE | Latest receipt (RS) date for the document. |
| `GroupID` | STRING | Smallest document number among the linked IS/BS/AS documents (graph connected up to 8 hops) within the company; documents of one invoice + its notes share a GroupID. |
| `GroupFlagComplete` | STRING | `Completed` only if every document in the GroupID group is Completed. This view keeps only `Non-Completed`, so the column is constant here. |
| `DayRange` | INT64 | Aging days: today (Asia/Bangkok) minus (MinReceiveDate if Completed, else invoiceDate) minus calCreditTerm. Positive = days overdue; used to pick the aging bucket (`dim_aging_rang` AgingDayMin/AgingDayMax). |
| `cfsDate` | DATE | `DATE(invoiceDate)`. |
| `minReceiptDate` | DATE | `MinReceiveDate` when flagComplete = 'Completed', else NULL. |
| `maxReceiptDate` | DATE | `MaxReceiveDate` when flagComplete = 'Completed', else NULL. |
| `minCustomerReceiptAgeDay` | INT64 | Minimum `ReceiptAgeDays` over all rows with the same `debcode` (window `PARTITION BY debcode`, not by company); NULL when the customer has no completed document. |
| `maxCustomerReceiptAgeDay` | INT64 | Maximum `ReceiptAgeDays` over all rows with the same `debcode`. |
| `ReceiptAgeDays` | INT64 | For Completed documents: days from invoiceDate to MaxReceiveDate; NULL when not completed. |
| `PoNumber` | STRING | Customer purchase-order or external order reference number. |
| `ReportName` | STRING | `dim_aging_rang.ReportName` for the row's aging bucket (join on AgingRangSK); NULL when no bucket matches (mds currently only has ranges for ag01 per the view_dim_aging comment). |
| `mirdesc` | STRING | Description copied from the referenced invoice. |
| `mirnotes` | STRING | Notes copied from the referenced invoice. |
| `ri_information` | STRING | Multi-line text, one numbered line per receipt (RS) document of the invoice, ordered by receive date: `n. (Y/N) <receipt no> / <receive date> / (<status code>) <status name>`. `(Y)` = receipt counts (FlagUse), `(N)` = excluded status. |
| `ri_amt` | STRING | Multi-line text (STRING, not numeric), one numbered line per receipt: `n. (Y/N) <receipt no> / <amount, 2 decimals> / เช็คปกติ/เช็คเด้ง [/ adjusted amount]`; `เช็คเด้ง` = bounced cheque, in which case the cheque-adjusted amount is appended. |

# How it is built

- Definition: `definitions/view/fact_view/view_aging_ri.sqlx` (`type: "view"`, tags `view`).
- Reads: [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_status_not_receive](/dimension/dim_status_not_receive.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md), [dimension_table.dim_aging_rang](/dimension/dim_aging_rang.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; its upstream tables are built first: `fact_mir_vs` -> `dim_aging` (tag `dimension_daily`) and `dim_status_not_receive`, `dim_invoice`, `dim_aging_rang`; `validated_mac5.chq/cql/mir/ar_s` and `curated_mih` are read via `ref()`. It re-derives the receipt/cheque adjustment logic that `dim_aging` also uses (CTEs `chq`, `edit_mir`).

# Examples

Total outstanding receivable per company and aging report bucket.

```sql
SELECT companyID, ReportName, COUNT(*) AS docs, SUM(OutStanding) AS outstanding
FROM `databuffet-nonprd.fact_view.view_aging_ri`
GROUP BY companyID, ReportName
ORDER BY companyID, outstanding DESC
```

The 100 most overdue open invoices with their payments so far.

```sql
SELECT companyID, cfsVnosID, debCode, dueDate, DayRange, TotalAmount, PaymentAmount, OutStanding, ri_information
FROM `databuffet-nonprd.fact_view.view_aging_ri`
WHERE cfsTypeID = 'IS' AND OutStanding > 0
ORDER BY DayRange DESC
LIMIT 100
```

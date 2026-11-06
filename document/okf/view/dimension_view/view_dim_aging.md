---
type: BigQuery View
title: "view_dim_aging"
description: "One row = one invoice (AgingSK) in the current accounts-receivable aging, with its channel, aging bucket and receipt-age measures."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_aging&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_aging
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_aging.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_aging.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Reporting view over [dim_aging](/dimension/dim_aging.md), the AR aging engine. It adds the four channel SKs (via [view_dim_channel](/view/dimension_view/view_dim_channel.md)), the aging bucket SK (`AgingRangSK`, from [dim_aging_rang](/dimension/dim_aging_rang.md)), `DayRange` (days past due) and per-customer receipt-age statistics.

Read by: [view_aging_ri](/view/fact_view/view_aging_ri.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md) and [dim_aging](/dimension/dim_aging.md) (the history snapshot step).

# Grain and key

One row = one invoice in the current aging: key `AgingSK` (QUALIFY ROW_NUMBER over `AgingSK` ordered by `ReceiptAgeDays` DESC keeps one row per `AgingSK`). `companyID`, `cfsVnosID`, `cfsTypeID` identify the invoice but are not the dedup key. The invoice `BFCN020/47` is excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingSK` | INT64 | SK of the invoice in the current [dim_aging](/dimension/dim_aging.md). Regenerated with ROW_NUMBER every night. |
| `AgingRangSK` | INT64 | SK of the aging bucket in [dim_aging_rang](/dimension/dim_aging_rang.md) whose [AgingDayMin, AgingDayMax] contains `DayRange`, matched within the same `CompanySK`; NULL when the company has no matching range. |
| `ChannelSK` | INT64 | SK of the channel in [dim_channel](/dimension/dim_channel.md), via [view_dim_channel](/view/dimension_view/view_dim_channel.md) joined on CompanySK + `cfsDep` = DepCode; NULL when no channel matches. |
| `ChannelFinanceSK` | INT64 | SK of the finance channel (`dim_channel_finance`), from view_dim_channel. |
| `ChannelSaleSK` | INT64 | SK of the sales channel (`dim_channel_sales`), from view_dim_channel. |
| `ChannelCostSK` | INT64 | SK of the cost channel (`dim_channel_cost`), from view_dim_channel. |
| `BillingSK` | INT64 | SK of the billing document in [fact_mir_vs](/fact/fact_mir_vs.md) (joined by invoice number); regenerated nightly. |
| `CustomerSK` | INT64 | SK of the customer in [dim_customer](/dimension/dim_customer.md) (stable MERGE SK). |
| `InvoiceSK` | INT64 | SK of the invoice in [dim_invoice](/dimension/dim_invoice.md) (stable MERGE SK). |
| `CompanySK` | INT64 | SK of the company in [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code. |
| `dueDate` | DATE | Due date: the MAC5 `mie` due date when present, otherwise `invoiceDate + transCreditTerm` (from dim_aging). |
| `realDueDate` | DATE | Computed due date `invoiceDate + transCreditTerm`, ignoring any mie override. |
| `invoiceDate` | DATE | Invoice date. |
| `cfsVnosID` | STRING | Invoice document number (cfs vnos / mih `mihVnos`); with `companyID` and `cfsTypeID` it identifies the invoice. |
| `cfsTypeID` | STRING | Invoice document type (MAC5 mih type of the aging document). |
| `cfsJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `cfsDep` | STRING | Department code of the document, used as the sales channel code. |
| `cfsPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `debCode` | STRING | Customer (debtor) code. |
| `debName` | STRING | Customer name (`debnamet` from dim_customer). |
| `calCreditTerm` | INT64 | Credit term in days used for the aging calculation (equals the invoice's `mihstanding`, same value as transCreditTerm). |
| `debCreditTerm` | INT64 | Credit term in days. |
| `transCreditTerm` | INT64 | Credit term in days stored on the invoice transaction (`mihstanding`). |
| `debLimit` | FLOAT64 | Credit limit of the customer in baht. |
| `debMemo` | STRING | Free-text memo on the customer. |
| `channel` | STRING | Always NULL in dim_aging (`CAST(NULL AS STRING)`). |
| `mihRef2` | STRING | Always NULL as an aging-schema placeholder. |
| `mihNote` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihRef1` | STRING | Distinct linked document numbers separated by pipes: credit/debit notes for IS rows and referenced invoices for BS/AS rows, with links in the closed-invoice exclusion list omitted. |
| `TotalAmount` | FLOAT64 | Invoice total amount of the IS document, rounded to 2 decimals. |
| `PaymentAmount` | FLOAT64 | Amount received against the invoice (dim_aging `RiAmount`): the full TotalAmount when the receipt is marked complete, else the sum of receipts. |
| `CreditNoteAmount` | FLOAT64 | Sum of credit notes (BS documents) linked to the invoice and not yet received (dim_aging `CnAmount`). |
| `DebitNoteAmount` | FLOAT64 | Sum of debit notes (AS documents) linked to the invoice and not yet received (dim_aging `DnAmount`). |
| `OutStanding` | FLOAT64 | Outstanding balance = TotalAmount - PaymentAmount + CreditNoteAmount + DebitNoteAmount, rounded to 2 decimals; 0 when the receipt is complete. |
| `flagComplete` | STRING | 'Completed' when OutStanding is between -1 and 1 (with a special rule for invoices dated before 2023 that checks RS receipts and cfs clear flags), otherwise 'Non-Completed'. |
| `MinReceiveDate` | DATE | Earliest receive date of the invoice (from mir / mie extract date). |
| `MaxReceiveDate` | DATE | Latest receive date of the invoice. |
| `GroupID` | STRING | Identifier of the group of linked invoices (chain of IS documents merged by dim_aging; minimum document number in the group). |
| `GroupFlagComplete` | STRING | 'Completed' only if every invoice in the same company + GroupID is Completed, else 'Non-Completed'. dim_aging_history keeps only 'Non-Completed' groups. |
| `DayRange` | INT64 | Days past due: (today - MinReceiveDate when Completed, else today - invoiceDate) minus calCreditTerm. Positive = overdue; used to pick the aging bucket. |
| `cfsDate` | DATE | `DATE(invoiceDate)`. |
| `minReceiptDate` | DATE | `DATE(MinReceiveDate)` when flagComplete = 'Completed', otherwise NULL. |
| `maxReceiptDate` | DATE | `DATE(MaxReceiveDate)` when flagComplete = 'Completed', otherwise NULL. |
| `minCustomerReceiptAgeDay` | INT64 | Minimum non-NULL ReceiptAgeDays across all rows of the same debCode (window over debcode only, not company). |
| `maxCustomerReceiptAgeDay` | INT64 | Maximum non-NULL ReceiptAgeDays across all rows of the same debCode (window over debcode only, not company). |
| `ReceiptAgeDays` | INT64 | Days from invoiceDate to MaxReceiveDate when Completed, otherwise NULL. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_aging.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_view.view_dim_channel](/view/dimension_view/view_dim_channel.md), [dimension_table.dim_aging_rang](/dimension/dim_aging_rang.md).

# Examples

Open (non-completed) overdue invoices by customer for one company:

```sql
SELECT debCode, SUM(OutStanding) AS outstanding
FROM `databuffet-nonprd.dimension_view.view_dim_aging`
WHERE companyID = 'ag01' AND flagComplete = 'Non-Completed' AND DayRange > 0
GROUP BY debCode
ORDER BY outstanding DESC
LIMIT 100
```

Outstanding by aging bucket:

```sql
SELECT AgingRangSK, COUNT(*) AS invoices, SUM(OutStanding) AS outstanding
FROM `databuffet-nonprd.dimension_view.view_dim_aging`
WHERE flagComplete = 'Non-Completed'
GROUP BY AgingRangSK
```

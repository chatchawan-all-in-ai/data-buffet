---
type: BigQuery View
title: "view_dim_aging_history"
description: "One row = one AR document in a non-completed group under a prior-day asatdate label, with SKs re-derived from natural keys."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_aging_history&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_aging_history
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_aging_history.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_aging_history.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Reporting view over [dim_aging_history](/dimension/dim_aging_history.md), the accumulating snapshot of AR documents in non-completed groups (prior-day labels retained for the latest day and month-ends). The source dims renumber `AgingSK` and `BillingSK` every night, so the view discards the stored keys and re-derives both from the natural key by joining the current [dim_aging](/dimension/dim_aging.md) and [fact_mir_vs](/fact/fact_mir_vs.md). It also adds the channel SKs from [view_dim_channel](/view/dimension_view/view_dim_channel.md).

# Grain and key

One row per asatdate + companyID + cfsVnosID + cfsTypeID (QUALIFY ROW_NUMBER over that key, ordered by ChannelSK, BillingSK; verified 0 duplicates inside a snapshot). Invoice `BFCN020/47` is excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `ChannelSK` | INT64 | SK of the channel in [dim_channel](/dimension/dim_channel.md), via [view_dim_channel](/view/dimension_view/view_dim_channel.md) joined on CompanySK + `cfsDep` = DepCode; NULL when no channel matches. |
| `ChannelFinanceSK` | INT64 | SK of the finance channel (`dim_channel_finance`), from view_dim_channel. |
| `ChannelSaleSK` | INT64 | SK of the sales channel (`dim_channel_sales`), from view_dim_channel. |
| `ChannelCostSK` | INT64 | SK of the cost channel (`dim_channel_cost`), from view_dim_channel. |
| `AgingSK` | INT64 | Re-derived: SK of the same invoice in the current [dim_aging](/dimension/dim_aging.md) via companyID + cfsVnosID + cfsTypeID; NULL if the invoice has since closed. |
| `BillingSK` | INT64 | Re-derived: BillingSK in [fact_mir_vs](/fact/fact_mir_vs.md) matched on companyID = company_id and cfsVnosID = mirbinvno; NULL if none. |
| `asatdate` | DATE | Stored prior-day snapshot label (latest label or a retained month-end); values were captured on `asatdate + 1 day`. |
| `AgingRangSK` | INT64 | Stored AgingRangSK from dim_aging_history (stable MERGE SK from dim_aging_rang), chosen using the capture-date `DayRange` (capture date = `asatdate + 1 day`). |
| `CustomerSK` | INT64 | SK of the customer in [dim_customer](/dimension/dim_customer.md) (stable MERGE SK). |
| `InvoiceSK` | INT64 | SK of the invoice in [dim_invoice](/dimension/dim_invoice.md) (stable MERGE SK). |
| `CompanySK` | INT64 | SK of the company in [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code (ag01/aa05/ab01/ac02/ak02). |
| `dueDate` | DATE | Due date: the MAC5 `mie` due date when present, otherwise `invoiceDate + transCreditTerm` (from dim_aging). |
| `realDueDate` | DATE | Computed due date `invoiceDate + transCreditTerm`, ignoring any mie override. |
| `invoiceDate` | DATE | Invoice date. |
| `cfsVnosID` | STRING | Invoice document number (cfs vnos / mih `mihVnos`); with companyID and cfsTypeID it is the natural key of an aging row. |
| `cfsTypeID` | STRING | Invoice document type (MAC5 mih type of the aging document). |
| `cfsJob` | STRING | Job code (`mihJob`) of the invoice. |
| `cfsDep` | STRING | Department code (`mihDep`) of the invoice; joined to channel `DepCode`. |
| `cfsPer` | STRING | Salesperson code (`mihPer`) of the invoice. |
| `debCode` | STRING | Customer code (`debcode`) of the invoice. |
| `debName` | STRING | Customer name (`debnamet` from dim_customer). Personal/company data - describe only. |
| `calCreditTerm` | INT64 | Credit term in days used for the aging calculation (equals the invoice's `mihstanding`, same value as transCreditTerm). |
| `debCreditTerm` | INT64 | Credit term in days on the customer master (`DEBcreditTerm` in dim_customer). |
| `transCreditTerm` | INT64 | Credit term in days stored on the invoice transaction (`mihstanding`). |
| `debLimit` | FLOAT64 | Customer credit limit (`debLimit` in dim_customer). |
| `debMemo` | STRING | Customer memo text from dim_customer. |
| `channel` | STRING | Always NULL in dim_aging (`CAST(NULL AS STRING)`); kept for report compatibility. |
| `mihRef2` | STRING | Always NULL in dim_aging (`CAST(NULL AS STRING)`); kept for report compatibility. |
| `mihNote` | STRING | Invoice notes (`mihNotes`). |
| `mihRef1` | STRING | Invoice reference (`InvoiceRef`, the mih ref1 of the aging document). |
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
| `DayRange` | INT64 | Stored days past due computed on the capture/run date (`asatdate + 1 day`): for 'Completed' documents `capture date - DATE(MinReceiveDate) - calCreditTerm`, otherwise `capture date - DATE(invoiceDate) - calCreditTerm`. Passed through from history, not recomputed today. |
| `cfsDate` | DATE | `DATE(invoiceDate)`. |
| `minReceiptDate` | DATE | `DATE(MinReceiveDate)` when flagComplete = 'Completed', otherwise NULL. |
| `maxReceiptDate` | DATE | `DATE(MaxReceiveDate)` when flagComplete = 'Completed', otherwise NULL. |
| `minCustomerReceiptAgeDay` | INT64 | Per-customer minimum ReceiptAgeDays stored during the capture run. |
| `maxCustomerReceiptAgeDay` | INT64 | Per-customer maximum ReceiptAgeDays stored during the capture run. |
| `ReceiptAgeDays` | INT64 | Days from invoiceDate to MaxReceiveDate when Completed, otherwise NULL. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_aging_history.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_view.view_dim_channel](/view/dimension_view/view_dim_channel.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_aging_history, view_dim_channel, dim_aging, fact_mir_vs. dim_aging_history is filled by the `dim_aging` operations (daily insert of `GroupFlagComplete = 'Non-Completed'`; keeps current-month yesterday plus previous month-ends).

# Examples

Outstanding on the latest snapshot per company:

```sql
SELECT companyID, SUM(OutStanding) AS outstanding
FROM `databuffet-nonprd.dimension_view.view_dim_aging_history`
WHERE asatdate = (SELECT MAX(asatdate) FROM `databuffet-nonprd.dimension_view.view_dim_aging_history`)
GROUP BY companyID
```

Month-end outstanding trend:

```sql
SELECT asatdate, SUM(OutStanding) AS outstanding
FROM `databuffet-nonprd.dimension_view.view_dim_aging_history`
GROUP BY asatdate
ORDER BY asatdate
```

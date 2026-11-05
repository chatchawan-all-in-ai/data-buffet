---
type: BigQuery Table
title: "dim_aging_history"
description: "One row = one AR document in a non-completed group, captured under the prior-day asatdate label; kept for the latest label and month-ends."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_aging_history&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_aging_history
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_aging.sqlx"
    title: "Dataform definition (dimension/dim_aging.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

History/snapshot table of AR aging, written by the operation in [dim_aging](/dimension/dim_aging.md) (`dim_aging.sqlx`): every night it inserts the rows of [view_dim_aging](/view/dimension_view/view_dim_aging.md) whose `GroupFlagComplete = 'Non-Completed'` under `asatdate = CURRENT_DATE('Asia/Bangkok') - 1`, then prunes old snapshots. The label is yesterday; the values are captured on the actual run date. It lets BI show the aging position at past month-ends (outstanding by bucket, overdue trend) and compare against the current dim_aging. It carries all `dim_aging` columns plus the view's computed `AgingRangSK`, `DayRange`, `cfsDate`, receipt dates and receipt-age columns (the channel SKs are dropped).

Read by: [view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md).

# Grain and key

One row = one document in one snapshot: key `asatdate` + (`companyID` + `cfsVnosID` + `cfsTypeID`). The source view excludes document `BFCN020/47` and keeps one row per `AgingSK` before insertion. Retention keeps only (a) the latest run date (yesterday) and (b) the last day of each earlier month. The table has no key constraint; the stored `AgingSK`/`BillingSK` are the values of the capture run and are not stable keys.

# Schema

| Column | Type | Description |
|---|---|---|
| `asatdate` | DATE | Snapshot label = the day before capture (`CURRENT_DATE('Asia/Bangkok') - 1`); the capture date is `asatdate + 1 day`. |
| `AgingSK` | INT64 | Aging surrogate key stored during the capture run. Regenerated every run in [dim_aging](/dimension/dim_aging.md), so stored values do not match the current `dim_aging` rows; [view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md) re-derives it. |
| `AgingRangSK` | INT64 | Aging-range bucket SK from [dim_aging_rang](/dimension/dim_aging_rang.md), chosen by `DayRange` between `AgingDayMin` and `AgingDayMax` for the same `CompanySK`. Stable (MERGE dim). Chosen using the capture-date `DayRange`, then frozen; NULL when no bucket matches. |
| `BillingSK` | INT64 | Billing-document surrogate key stored during the capture run (from [fact_mir_vs](/fact/fact_mir_vs.md)); regenerated every run there, so the stored value is not stable. The view re-derives it from the natural key. |
| `CustomerSK` | INT64 | Customer surrogate key from [dim_customer](/dimension/dim_customer.md), joined on `debcode` (the invoice's `mihCus`) and `CompanySK`. NULL when no customer matches. |
| `InvoiceSK` | INT64 | Invoice surrogate key from [dim_invoice](/dimension/dim_invoice.md), joined on document number (`mihVnos`) and `CompanySK` (first SK per company and document number). |
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
| `transCreditTerm` | INT64 | Document credit term captured from `dim_aging`; see its [schema](/dimension/dim_aging.md#schema) for the calculation. |
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
| `OutStanding` | FLOAT64 | Remaining balance captured from `dim_aging`; see its [schema](/dimension/dim_aging.md#schema) for the calculation. Stored at capture time and not recalculated when read. |
| `flagComplete` | STRING | 'Completed' when `OutStanding` is between -1 and 1, else 'Non-Completed'. For invoices dated before 2023 that are still non-complete, a legacy check on `cfs` (`cfsclearsum = -1` and `cfsclearall = -1`) can flip it to 'Completed'. |
| `MinReceiveDate` | DATE | Earliest receipt date for the document (from RS `mir` rows, or the cheque `extract_date` when cheque extraction applies). |
| `MaxReceiveDate` | DATE | Latest receipt date for the document (same sources as `MinReceiveDate`). |
| `GroupID` | STRING | Id of the invoice group: the smallest document number connected through invoice <-> credit/debit-note links (graph closure computed with hop_2 / hop_4 / hop_8 joins, so up to 8 hops). Scoped per company. |
| `GroupFlagComplete` | STRING | 'Completed' only if every document in the same (`CompanyID`, `GroupID`) is 'Completed'. Snapshots contain only 'Non-Completed' groups; an individual document may be 'Completed'. |
| `DayRange` | INT64 | Days past due computed in [view_dim_aging](/view/dimension_view/view_dim_aging.md) on the capture/run date (`CURRENT_DATE('Asia/Bangkok')`, one day after `asatdate`): for 'Completed' documents `capture date - DATE(MinReceiveDate) - calCreditTerm`, otherwise `capture date - DATE(invoiceDate) - calCreditTerm`. Positive = overdue; the stored value is not recalculated when read. |
| `cfsDate` | DATE | `DATE(invoiceDate)`, the document date. |
| `minReceiptDate` | DATE | `MinReceiveDate` when `flagComplete = 'Completed'`, else NULL. |
| `maxReceiptDate` | DATE | `MaxReceiveDate` when `flagComplete = 'Completed'`, else NULL. |
| `minCustomerReceiptAgeDay` | INT64 | Smallest `ReceiptAgeDays` of the same customer code (`debcode`) across all rows of `view_dim_aging` before the `Non-Completed` snapshot filter (window over customer, ignoring NULLs). |
| `maxCustomerReceiptAgeDay` | INT64 | Largest `ReceiptAgeDays` of the same customer code across all rows of `view_dim_aging` before the `Non-Completed` snapshot filter (`LAST_VALUE` over ordered rows, ignoring NULLs). |
| `ReceiptAgeDays` | INT64 | For 'Completed' rows, days from `invoiceDate` to `MaxReceiveDate` (how long the customer took to pay); NULL otherwise. |

# How it is built

- Definition: `definitions/dimension/dim_aging.sqlx` (`type: "operations"`, tag `dimension_daily`); the post-step of the dim_aging operation writes this table; the target pre-exists in BigQuery.
- Reads: [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md).
- Incremental append (no separate file); steps each run: DELETE `asatdate >= run_date`, INSERT today's non-completed rows from `view_dim_aging` (`run_date = CURRENT_DATE('Asia/Bangkok') - 1`), then DELETE rows of the current month older than run_date and rows of earlier months that are not the month's last day. Runs after `dim_aging` is rebuilt in the same file.

# Examples

Outstanding by aging bucket at the last snapshot of each month (month-end snapshots only).

```sql
SELECT asatdate, companyID, AgingRangSK, COUNT(*) AS docs, ROUND(SUM(OutStanding), 2) AS outstanding
FROM `databuffet-nonprd.dimension_table.dim_aging_history`
WHERE asatdate = LAST_DAY(asatdate)
GROUP BY asatdate, companyID, AgingRangSK
ORDER BY asatdate, companyID, AgingRangSK;
```

Customers with the most overdue outstanding on the latest snapshot.

```sql
SELECT companyID, debCode, ROUND(SUM(OutStanding), 2) AS overdue
FROM `databuffet-nonprd.dimension_table.dim_aging_history`
WHERE asatdate = (SELECT MAX(asatdate) FROM `databuffet-nonprd.dimension_table.dim_aging_history`)
  AND DayRange > 0 AND cfsTypeID = 'IS'
GROUP BY companyID, debCode
ORDER BY overdue DESC
LIMIT 20;
```

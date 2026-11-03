---
type: BigQuery View
title: "export_view_dim_aging_history"
description: "One row = one invoice of one company on one as-at date of the receivables aging snapshot, exposed for the Pub/Sub export of the AI team sample table dimension_view.view_dim_aging_history with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_aging_history&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_aging_history
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_aging_history.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_aging_history.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `view_dim_aging_history` to topic `export-ta-view_dim_aging_history`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one invoice of one company on one as-at date of the receivables aging snapshot: key `asatdate`, `companyID`, `cfsVnosID` (unique); `row_key` is the JSON of that key. Rows on 2026-11-02: 1,103,941.

# Schema

| Column | Type | Description |
|---|---|---|
| `asatdate` | DATE | Stored prior-day snapshot label (latest label or a retained month-end); values were captured on `asatdate + 1 day`. |
| `CustomerSK` | INT64 | SK of the customer in [dim_customer](/dimension/dim_customer.md) (stable MERGE SK). |
| `InvoiceSK` | INT64 | SK of the invoice in [dim_invoice](/dimension/dim_invoice.md) (stable MERGE SK). |
| `CompanySK` | INT64 | SK of the company in [dim_company](/dimension/dim_company.md). |
| `ChannelSK` | INT64 | SK of the channel in [dim_channel](/dimension/dim_channel.md), via [view_dim_channel](/view/dimension_view/view_dim_channel.md) joined on CompanySK + `cfsDep` = DepCode; NULL when no channel matches. |
| `AgingRangSK` | INT64 | Stored AgingRangSK from dim_aging_history (stable MERGE SK from dim_aging_rang), chosen using the capture-date `DayRange` (capture date = `asatdate + 1 day`). |
| `transCreditTerm` | INT64 | Credit term in days stored on the invoice transaction (`mihstanding`). |
| `dueDate` | DATE | Due date: the MAC5 `mie` due date when present, otherwise `invoiceDate + transCreditTerm` (from dim_aging). |
| `realDueDate` | DATE | Computed due date `invoiceDate + transCreditTerm`, ignoring any mie override. |
| `cfsVnosID` | STRING | Invoice document number (cfs vnos / mih `mihVnos`); with companyID and cfsTypeID it is the natural key of an aging row. |
| `TotalAmount` | FLOAT64 | Invoice total amount of the IS document, rounded to 2 decimals. |
| `CreditNoteAmount` | FLOAT64 | Sum of credit notes (BS documents) linked to the invoice and not yet received (dim_aging `CnAmount`). |
| `DebitNoteAmount` | FLOAT64 | Sum of debit notes (AS documents) linked to the invoice and not yet received (dim_aging `DnAmount`). |
| `OutStanding` | FLOAT64 | Outstanding balance = TotalAmount - PaymentAmount + CreditNoteAmount + DebitNoteAmount, rounded to 2 decimals; 0 when the receipt is complete. |
| `flagComplete` | STRING | 'Completed' when OutStanding is between -1 and 1 (with a special rule for invoices dated before 2023 that checks RS receipts and cfs clear flags), otherwise 'Non-Completed'. |
| `GroupFlagComplete` | STRING | 'Completed' only if every invoice in the same company + GroupID is Completed, else 'Non-Completed'. dim_aging_history keeps only 'Non-Completed' groups. |
| `DayRange` | INT64 | Stored days past due computed on the capture/run date (`asatdate + 1 day`): for 'Completed' documents `capture date - DATE(MinReceiveDate) - calCreditTerm`, otherwise `capture date - DATE(invoiceDate) - calCreditTerm`. Passed through from history, not recomputed today. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_aging_history.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_aging_history](/view/dimension_view/view_dim_aging_history.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `dimension_view.view_dim_aging_history`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_aging_history`
GROUP BY row_key
HAVING n > 1
```

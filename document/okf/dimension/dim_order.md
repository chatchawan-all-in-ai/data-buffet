---
type: BigQuery Table
title: "dim_order"
description: "One row = one MAC5 sales order (document type PS) per company with header attributes, status text and a derived fulfilment status (On Order / In Process / Complete)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_order&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_order
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_order.sqlx"
    title: "Dataform definition (dimension/dim_order.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Sales-order dimension. Each row is a `curated_mih` header of type PS (sales order) from the last four years with its status name and colour from `ar_s`, salesperson name from `per`, delivery/key dates and an `OrderStatus` computed by comparing ordered quantities per item (PS lines) with invoiced quantities (IS lines whose `milLinkVcno` points to the order). It is the source of `OrderSK` for [fact_order](/fact/fact_order.md), [fact_order_store](/fact/fact_order_store.md), [fact_backlog_store](/fact/fact_backlog_store.md), [fact_invoice_store](/fact/fact_invoice_store.md) and [fact_transcation](/fact/fact_transcation.md); [dim_invoice](/dimension/dim_invoice.md) links invoices to it, and [view_dim_order](/view/dimension_view/view_dim_order.md) exposes it.

Used by: [fact_table.fact_backlog_store](/fact/fact_backlog_store.md), [fact_table.fact_invoice_store](/fact/fact_invoice_store.md), [fact_table.fact_order](/fact/fact_order.md), [fact_table.fact_order_store](/fact/fact_order_store.md), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [dimension_view.view_dim_order](/view/dimension_view/view_dim_order.md), [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [fact_table.fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per (`CompanySK`, `mihYear`, `mihMonth`, `mihDay`, `mihType` = 'PS', `mihVnos`, `mihCus` with NULL treated as empty). `OrderSK` is a stable surrogate key (existing orders keep it; new ones get `max_sk + ROW_NUMBER()`). Only orders dated from 1 January four years ago are loaded.

# Schema

| Column | Type | Description |
|---|---|---|
| `OrderSK` | INT64 | Stable surrogate key of the order; never regenerated, stored in facts. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code. |
| `mix_date` | DATE | Order date built from `mihYear`/`mihMonth`/`mihDay`. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihDay` | INT64 | Day part of the document date. |
| `mihType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `mihCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `mihJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `mihRef1` | STRING | Reference document number 1 for the source quotation or sales order. |
| `mihRef2` | STRING | Customer purchase-order or external order reference number. |
| `mihRef3` | STRING | Free-text reference 3 of the document. |
| `mihCancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihStatus` | INT64 | Document status code; meaning in `ar_s` for sales types and `ap_s` for purchase types (e.g. 26 = approved sales order, 30 = VAT sale, 32 = cancelled tax invoice). |
| `StatusName` | STRING | Thai status name. |
| `memoExtract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `mihMemoNew` | STRING | Document memo with the tag enclosed in `฿` signs removed, or NULL when no text remains. |
| `mihStatusDesc` | STRING | Pass-through of `curated_mih.mihstatus_desc` (status description derived upstream). |
| `OrderStatus` | STRING | Fulfilment status computed here: per item, 'On Order' if no invoice line links to it, 'Complete' if invoiced quantity >= ordered quantity, else 'In Process'; per order, any 'In Process' item makes 'In Process', else any 'On Order' makes 'On Order', else 'Complete'. NULL when the order has no PS lines. |
| `mihNotes` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihDesc` | STRING | Free-text document description. |
| `mihKeydate` | DATETIME | Date and time the document was keyed. |
| `mihDelvdate` | DATETIME | Requested delivery date. |
| `mihClearum` | INT64 | Flag: outstanding quantities of the document cleared (0 = still open). |
| `mihExtrasum` | FLOAT64 | Deposit amount deducted on the document, excluding VAT. |
| `mihPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `pernamet` | STRING | Employee name in Thai (first name, surname and nickname in parentheses). |
| `mihBl` | INT64 | Billing-note flag of the document. |
| `StatusColorBg` | INT64 | Background colour of the status in the ERP, as a Windows RGB integer. |

# How it is built

- Definition: `definitions/dimension/dim_order.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.per](/validated/validated_mac5/per.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `OrderSK` found via (year, month, day, type, `mihVnos`, `mihCus`, `CompanySK`). Source is all PS headers within the last 4 years (from 1 January) with no incremental window; updates attributes, inserts new orders, no delete. Runs after `dim_company`; the target table pre-exists in BigQuery.

# Examples

Open orders per company by fulfilment status for the current year.

```sql
SELECT companyID, OrderStatus, COUNT(*) AS orders
FROM `databuffet-nonprd.dimension_table.dim_order`
WHERE mihCancel <> -1 AND mihYear = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY companyID, OrderStatus
ORDER BY companyID, OrderStatus;
```

Orders still not fully invoiced, oldest first.

```sql
SELECT companyID, mihVnos, mix_date, mihCus, OrderStatus, StatusName, mihDelvdate
FROM `databuffet-nonprd.dimension_table.dim_order`
WHERE OrderStatus IN ('On Order', 'In Process') AND mihCancel <> -1
ORDER BY mix_date
LIMIT 100;
```

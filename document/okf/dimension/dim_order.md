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
| `mihYear` | INT64 | Year part of the order date (pass-through of `curated_mih.mihYear`). |
| `mihMonth` | INT64 | Month part of the order date. |
| `mihDay` | INT64 | Day part of the order date. |
| `mihType` | STRING | Document type; always 'PS' (sales order) in this table. |
| `mihVnos` | STRING | Order document number. |
| `mihCus` | STRING | Customer code on the order (joins to `dim_customer.debcode`). |
| `mihJob` | STRING | Job code of the header (pass-through; likely job/project code, inferred). |
| `mihRef1` | STRING | Reference number 1 of the header (pass-through). |
| `mihRef2` | STRING | Reference number 2 of the header (pass-through). |
| `mihRef3` | STRING | Reference number 3 of the header (pass-through). |
| `mihCancel` | INT64 | Cancel flag (-1 = cancelled, 0 = active). |
| `mihStatus` | INT64 | Status code of the order (`curated_mih.mihStatus`), looked up in `ar_s`. |
| `StatusName` | STRING | Status name from `ar_s.ar_snamet` for `mihStatus` (company-specific). |
| `memoExtract` | STRING | Pass-through of `curated_mih.memoExtract`; Meaning not documented in the repo. |
| `mihMemoNew` | STRING | Pass-through of `curated_mih.mihMemoNew`; Meaning not documented in the repo (likely free-text memo). |
| `mihStatusDesc` | STRING | Pass-through of `curated_mih.mihstatus_desc` (status description derived upstream). |
| `OrderStatus` | STRING | Fulfilment status computed here: per item, 'On Order' if no invoice line links to it, 'Complete' if invoiced quantity >= ordered quantity, else 'In Process'; per order, any 'In Process' item makes 'In Process', else any 'On Order' makes 'On Order', else 'Complete'. NULL when the order has no PS lines. |
| `mihNotes` | STRING | Free-text notes of the header. |
| `mihDesc` | STRING | Free-text description of the header. |
| `mihKeydate` | DATETIME | Date/time the order was keyed in (`curated_mih.mihKeydate`, DATETIME); NULL for rows outside the refresh window that were loaded before the column existed. |
| `mihDelvdate` | DATETIME | Requested delivery date/time of the order (`curated_mih.mihDelvdate`, DATETIME). |
| `mihClearum` | INT64 | Pass-through of `curated_mih.mihClearum`; Meaning not documented in the repo. |
| `mihExtrasum` | FLOAT64 | Extra amount on the document (`curated_mih.mihExtrasum`); meaning not documented in the repo. |
| `mihPer` | STRING | Salesperson code of the order header. |
| `pernamet` | STRING | Salesperson Thai name from `validated_mac5.per` (join `mihPer = percode`, company). |
| `mihBl` | INT64 | Pass-through of `curated_mih.mihBl`; Meaning not documented in the repo. |
| `StatusColorBg` | INT64 | Background colour code of the status from `ar_s.ar_scolb` (INT64), used by reports to colour status cells. |

# How it is built

- Definition: `definitions/dimension/dim_order.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.per](/validated/validated_mac5/per.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `OrderSK` found via (year, month, day, type, `mihVnos`, `mihCus`, `CompanySK`). Source is all PS headers within the last 4 years (from 1 January) with no incremental window; updates attributes, inserts new orders, no delete. Runs after `dim_company`; the target table pre-exists in BigQuery.
- Approximate size (BigQuery metadata, 2026-10-31): 1,400,902 rows, 839.3 MB.

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

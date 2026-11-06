---
type: BigQuery View
title: "view_dim_order"
description: "One row = one sales order (OrderSK, MAC5 PS document) with status, order type, ship-to and an expiry flag."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_order&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_order
tags: ["view", "dimension_view", "mac5", "mds"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_order.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_order.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Order dimension for sales/backlog reporting: [dim_order](/dimension/dim_order.md) plus `OrderType` (via `fn_order_type` on `mihref2`), `CustomerShipTo` (`mih2pos` from MAC5 mih2) and `FlagExpire` (document older than the MDS expiry rule for its prefix).

Read by: [export_view_dim_order](/view/pub_sub/export_view_dim_order.md).

# Grain and key

One row = one sales order: key `OrderSK` (unique; `QUALIFY ROW_NUMBER()` over `OrderSK` ordered by `mih2pos` DESC, so one ship-to is chosen when several exist). dim_order natural key: company + `mihYear`/`mihMonth`/`mihDay` + `mihType` ('PS') + `mihVnos` + `mihCus` (NULL treated as empty).

# Schema

| Column | Type | Description |
|---|---|---|
| `OrderSK` | INT64 | Stable SK of the order in dim_order (MERGE). |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `mix_date` | DATE | Document date, `PARSE_DATE('%Y%m%d', CONCAT(mihYear, mihMonth, mihDay))`. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihDay` | INT64 | Day part of the document date. |
| `mihType` | STRING | Document type code (`PS` = sales order). |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `mihCus` | STRING | Customer code, matching `deb.debcode`. |
| `mihJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `mihRef1` | STRING | Reference document number 1 for the source quotation or sales order. |
| `mihRef2` | STRING | Customer purchase-order or external order reference number. |
| `mihRef3` | STRING | Free-text reference 3 of the document. |
| `mihCancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihStatus` | INT64 | Document status code from the header, with sales status meanings in `ar_s`. |
| `StatusName` | STRING | Thai status name. |
| `memoExtract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `mihMemoNew` | STRING | Document memo with the tag enclosed in `฿` signs removed, or NULL when no text remains. |
| `mihStatusDesc` | STRING | Status description text from the mih row (`mihstatus_desc`). |
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
| `OrderType` | STRING | Order type derived by `fn_order_type(mihref2)`. |
| `CustomerShipTo` | STRING | Ship-to location of the order (customer branch, plot or house). |
| `FlagExpire` | STRING | 'Yes' when order age in days (today - mix_date) exceeds the MDS `ExpireDays` for the document prefix; 'No' otherwise or when no rule exists. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_order.sqlx` (`type: "view"`, tags `view`).
- Reads: `function_dataset.fn_order_type` (UDF), [dimension_table.dim_order](/dimension/dim_order.md), [validated_mac5.mih2](/validated/validated_mac5/mih2.md), `mds_dataset.mds_data_document_expire_rule_master` (master data loaded outside this repo).

# Examples

Open orders that have expired:

```sql
SELECT OrderSK, mihVnos, mix_date, OrderStatus, OrderType
FROM `databuffet-nonprd.dimension_view.view_dim_order`
WHERE FlagExpire = 'Yes' AND (OrderStatus IS NULL OR OrderStatus != 'Complete')
```

Orders by status for the last 60 days:

```sql
SELECT OrderStatus, COUNT(*) AS orders
FROM `databuffet-nonprd.dimension_view.view_dim_order`
WHERE mix_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 60 DAY)
GROUP BY OrderStatus
```

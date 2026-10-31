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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Order dimension for sales/backlog reporting: [dim_order](/dimension/dim_order.md) plus `OrderType` (via `fn_order_type` on `mihref2`), `CustomerShipTo` (`mih2pos` from MAC5 mih2) and `FlagExpire` (document older than the MDS expiry rule for its prefix). The business meaning of the flag is documented in overview/business-flags.md.

# Grain and key

One row per `OrderSK` (QUALIFY ROW_NUMBER over OrderSK ordered by mih2pos DESC, so one ship-to is chosen when several exist). dim_order natural key: mihYear/mihMonth/mihDay/mihType/mihVnos (+ company).

# Schema

| Column | Type | Description |
|---|---|---|
| `OrderSK` | INT64 | Stable SK of the order in dim_order (MERGE). |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `mix_date` | DATE | Document date, `PARSE_DATE('%Y%m%d', CONCAT(mihYear, mihMonth, mihDay))`. |
| `mihYear` | INT64 | Year of the document date. |
| `mihMonth` | INT64 | Month of the document date. |
| `mihDay` | INT64 | Day of the document date (MAC5 mih). |
| `mihType` | STRING | MAC5 document type code (e.g. IS invoice, BS credit note, AS debit note, QS quotation, PS order). |
| `mihVnos` | STRING | Document number (vnos). |
| `mihCus` | STRING | Customer code (`debcode`) on the document. |
| `mihJob` | STRING | Job code on the document. |
| `mihRef1` | STRING | Reference 1 on the document (for invoices, the order number it references). |
| `mihRef2` | STRING | Reference 2 on the document. |
| `mihRef3` | STRING | Reference 3 on the order document. |
| `mihCancel` | INT64 | Cancel flag on the order (STRING in this table; -1 style values as in MAC5). |
| `mihStatus` | INT64 | Status code of the document (joined to ar_s/ap_s for the name). |
| `StatusName` | STRING | Status name from MAC5 ar_s (`ar_snamet`) for `mihStatus`. |
| `memoExtract` | STRING | Memo-extract text on the order (curated_mih `memoExtract`). |
| `mihMemoNew` | STRING | New-memo text on the order (curated_mih `mihMemoNew`). |
| `mihStatusDesc` | STRING | Status description text from the mih row (`mihstatus_desc`). |
| `OrderStatus` | STRING | Fulfilment status computed in dim_order from PS vs IS quantities per item: 'In Process' if any item partly delivered, else 'On Order' if any item undelivered, else 'Complete'. |
| `mihNotes` | STRING | Free-text notes on the document. |
| `mihDesc` | STRING | Description text on the document. |
| `mihKeydate` | DATETIME | Date/time the order was keyed in. |
| `mihDelvdate` | DATETIME | Requested delivery date/time. |
| `mihClearum` | INT64 | Clear-sum value from mih (MAC5 `mihClearum`); meaning not documented beyond the name. |
| `mihExtrasum` | FLOAT64 | Extra-sum amount from mih (MAC5 `mihExtrasum`); meaning not documented beyond the name. |
| `mihPer` | STRING | Salesperson code on the document. |
| `pernamet` | STRING | Salesperson name from the MAC5 `per` table (personal data). |
| `mihBl` | INT64 | MAC5 `mihBl` flag on the order; Meaning not documented in the repo. |
| `StatusColorBg` | INT64 | Background colour code of the status from MAC5 ar_s (`ar_scolb`). |
| `OrderType` | STRING | Order type derived by `fn_order_type(mihref2)`. |
| `CustomerShipTo` | STRING | Ship-to code `mih2pos` from MAC5 mih2 matched on the order's date, type, customer and number (greatest value if several). |
| `FlagExpire` | STRING | 'Yes' when order age in days (today - mix_date) exceeds the MDS `ExpireDays` for the document prefix; 'No' otherwise or when no rule exists. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_order.sqlx` (`type: "view"`, tags `view`).
- Reads: `function_dataset.fn_order_type` (UDF), [dimension_table.dim_order](/dimension/dim_order.md), [validated_mac5.mih2](/validated/validated_mac5/mih2.md), `mds_dataset.mds_data_document_expire_rule_master` (master data loaded outside this repo).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_order (operations MERGE, stable SK, tag `dimension_daily`), validated_mac5.mih2, MDS `mds_data_document_expire_rule_master`, and UDF `fn_order_type`.

# Examples

Open orders that have expired:

```sql
SELECT OrderSK, mihVnos, mix_date, OrderStatus, OrderType
FROM `databuffet-nonprd.dimension_view.view_dim_order`
WHERE FlagExpire = 'Yes' AND OrderStatus != 'Complete'
```

Orders by status for the last 60 days:

```sql
SELECT OrderStatus, COUNT(*) AS orders
FROM `databuffet-nonprd.dimension_view.view_dim_order`
WHERE mix_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 60 DAY)
GROUP BY OrderStatus
```

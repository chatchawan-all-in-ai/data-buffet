---
type: BigQuery Table
title: "fact_invoice_store"
description: "One row = one product line of an invoice (IS) per salesperson share (milPer) for ag01/ab01, with invoice, order, product, customer and store SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_invoice_store&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_invoice_store
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_invoice_store.sqlx"
    title: "Dataform definition (fact/fact_invoice_store.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Invoice-line fact sliced by store/warehouse: IS lines from `curated_mil` + `curated_mih`, linked to the invoice ([dim_invoice](/dimension/dim_invoice.md)) and, through `milLinkVcno`, to the order ([dim_order](/dimension/dim_order.md)). It answers which products were invoiced per store, per salesperson share and date. It is the invoice counterpart of [fact_order_store](/fact/fact_order_store.md) and [fact_backlog_store](/fact/fact_backlog_store.md).

Read by: none in this repository.

# Grain and key

One row = one product line of an IS invoice per salesperson share (`milPer`): key `FactInvoiceStoreSK` (see [Schema](#schema) for key generation). The IS side of `curated_mil` splits a line across salespeople by `percent_sale`, one row per share. Window: 4 years truncated to start-of-year on the invoice date (not filtered by order). Only company_id ag01 and ab01; only products whose `TypeMarketing` is not 'Sourcing' (products with no marketing type are dropped too); lines with `milstype <> 3`, product code not starting with the Thai letter bo and not `TEST%`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactInvoiceStoreSK` | INT64 | Stable row key: FARM_FINGERPRINT of the typed company/date/type/invoice/line/salesperson-share grain plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `company_id` | STRING | MAC5 company code; only 'ag01' and 'ab01' are loaded. |
| `mix_date` | DATE | Invoice date: SAFE.PARSE_DATE of mihYear, mihMonth, mihDay; partition column. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihDay` | INT64 | Day part of the document date. |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `InvoiceSK` | INT64 | Surrogate key of [dim_invoice](/dimension/dim_invoice.md) (milType 'IS', company + mihVnos, latest InvoiceSK); NULL if unmatched. |
| `OrderSK` | INT64 | OrderSK of the order whose `mihVnos = milLinkVcno`; -1 when none. |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`debcode = mihCus`, same company); NULL when unmatched. |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (case-insensitive product code match); rows without a product (or with TypeMarketing 'Sourcing') are dropped by an INNER JOIN, so never NULL. |
| `StoreSK` | INT64 | Surrogate key of [dim_store](/dimension/dim_store.md) (warehouse/branch) matched on company and store code; -1 when the store code is not in dim_store. |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milListNo` | INT64 | Line number within the document. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milDesc` | STRING | Free-text line description. |
| `milSto` | STRING | Warehouse (store) code the line is issued from, matching `sto` store codes. |
| `milLinkVcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `milLinkVcType` | STRING | Document type of the linked source document (e.g. `PS`, `PP`). |
| `milQuan` | FLOAT64 | Allocated quantity from curated_mil, passed through per salesperson share. |
| `milPer` | STRING | Salesperson code of the line (the IS line is split by salesperson share). |
| `percent_sale` | STRING | Salesperson share (percentage, stored as STRING) already applied to milQuan by curated_mil. |
| `FlagFree` | STRING | 'Yes' when `milsum = 0` OR `ProductGroupMAC5 = '5000'`; else 'No'. |

# How it is built

- Definition: `definitions/fact/fact_invoice_store.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactInvoiceStoreSK`.
- Storage options: `{"partitionBy": "mix_date", "clusterBy": ["FactInvoiceStoreSK"]}`.
- Reads: [dimension_table.dim_order](/dimension/dim_order.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_store](/dimension/dim_store.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactInvoiceStoreSK`, partition `mix_date`), after `dim_order`, `dim_invoice`, `dim_customer`, `dim_product_master`, `dim_company`, `dim_store`.

# Examples

Invoiced quantity per store for a month (excluding free lines).
```sql
SELECT StoreSK, SUM(milQuan) AS qty
FROM `databuffet-nonprd.fact_table.fact_invoice_store`
WHERE mix_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-31' AND FlagFree = 'No'
GROUP BY StoreSK;
```
Invoice lines that have no order.
```sql
SELECT mihVnos, milListNo, milStk
FROM `databuffet-nonprd.fact_table.fact_invoice_store`
WHERE OrderSK = -1 AND mix_date >= DATE '2026-10-01';
```

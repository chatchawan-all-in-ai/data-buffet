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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Invoice-line fact sliced by store/warehouse: IS lines from `curated_mil` + `curated_mih`, linked to the invoice ([dim_invoice](/dimension/dim_invoice.md)) and, through `milLinkVcno`, to the order ([dim_order](/dimension/dim_order.md)). It answers which products were invoiced per store, per salesperson share and date. It is the invoice counterpart of [fact_order_store](/fact/fact_order_store.md) and [fact_backlog_store](/fact/fact_backlog_store.md); no other table reads it.

Used by / context: used by nothing else in the repo.

# Grain and key

One row per `FactInvoiceStoreSK` (ROW_NUMBER over CompanySK, date parts, milType, mihVnos, milListNo, milPer). The grain includes `milPer` because the IS side of `curated_mil` splits a line across salespeople by `percent_sale`. Window: 4 years truncated to start-of-year on the invoice date (not filtered by order). Only company_id ag01 and ab01, only products whose `TypeMarketing` is not 'Sourcing', and (store facts) lines with `milstype <> 3`, product code not starting with the Thai letter bo, and not `TEST%`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactInvoiceStoreSK` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, date parts, milType, mihVnos, milListNo, milPer. Regenerates daily. |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md). |
| `company_id` | STRING | MAC5 company code; only 'ag01' and 'ab01' are loaded. |
| `mix_date` | DATE | Invoice date: SAFE.PARSE_DATE of mihYear, mihMonth, mihDay; partition column. |
| `mihYear` | INT64 | Year of the document header (curated_mih). |
| `mihMonth` | INT64 | Month of the document header (curated_mih). |
| `mihDay` | INT64 | Day of the document header (curated_mih). |
| `mihVnos` | STRING | Invoice document number (curated_mih). |
| `InvoiceSK` | INT64 | Surrogate key of [dim_invoice](/dimension/dim_invoice.md) (milType 'IS', company + mihVnos, latest InvoiceSK); NULL if unmatched. |
| `OrderSK` | INT64 | OrderSK of the order whose `mihVnos = milLinkVcno`; -1 when none. |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`debcode = mihCus`, same company); NULL when unmatched. |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (case-insensitive product code match); rows without a product (or with TypeMarketing 'Sourcing') are dropped by an INNER JOIN, so never NULL. |
| `StoreSK` | INT64 | Surrogate key of [dim_store](/dimension/dim_store.md) (warehouse/branch) matched on company and store code; -1 when the store code is not in dim_store. |
| `milType` | STRING | Document type from curated_mil. |
| `milListNo` | INT64 | Line number within the document (curated_mil). |
| `milStk` | STRING | Product code of the line. |
| `milDesc` | STRING | Line description text from curated_mil. |
| `milSto` | STRING | Store/warehouse code of the line (joins `dim_store.StoreCode`). |
| `milLinkVcno` | STRING | Document number the line links to (the originating order); join key to dim_order. |
| `milLinkVcType` | STRING | Document type of the linked document (curated_mil); meaning inferred from the name. |
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
- Approximate size (BigQuery metadata, 2026-10-31): 2,230,430 rows, 539.9 MB.

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

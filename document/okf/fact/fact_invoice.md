---
type: BigQuery Table
title: "fact_invoice"
description: "One row = one product (milStk) on one invoice-type document (IS/BS/AS/QS) per customer and link number per company, within the last 4 years."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_invoice&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_invoice
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_invoice.sqlx"
    title: "Dataform definition (fact/fact_invoice.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Invoice-line fact: lines of IS, BS, AS and QS documents from `curated_mil`, joined to `view_dim_invoice` for InvoiceSK, to the originating order line ([fact_order](/fact/fact_order.md), de-duplicated), the quotation, customer and company. It answers what was invoiced/billed and how it ties back to the order and quotation.

Read by: [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one product on one invoice-type document (IS/BS/AS/QS) per customer and link number (`milLinkVcno`), per company: key `FactInvoiceSK`. Its stable value is a typed business-key hash over company, invoice date, type, invoice number, customer, lower-case stock code and `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). The group-by also includes `milLinkVcno`. Lines are INNER JOINed to `view_dim_invoice` (date, type, vnos, customer, milLinkVcno, company), so lines whose invoice is not found there are dropped. Window: `mix_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR)`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactInvoiceSK` | INT64 | Stable row key: FARM_FINGERPRINT of typed company/date/type/invoice/customer/stock fields plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). |
| `InvoiceSK` | INT64 | Surrogate key from `view_dim_invoice` (join on date, type, vnos, customer, milLinkVcno, company). |
| `OrderSK` | INT64 | OrderSK of the linked order line from [fact_order](/fact/fact_order.md); NULL if none. |
| `FactOrderSK` | INT64 | [fact_order](/fact/fact_order.md).FactOrderSk of the linked order line selected by highest `occ` within the matching order grain. |
| `QuotationSK` | INT64 | QuotationSK inherited via fact_order. |
| `FactQuotationSK` | INT64 | FactQuotationSK inherited via fact_order ([fact_quotation](/fact/fact_quotation.md)). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code. |
| `mix_date` | DATE | Business date of the invoice (PARSE_DATE of year/month/day). |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milMonth` | INT64 | Month part of the document date. |
| `milDay` | INT64 | Day part of the document date. |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milvnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milLinkVcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `milQuan` | FLOAT64 | SUM of `curated_mil.milQuan` over the grain; the salesperson share is already applied on ag01 split-sale lines. |
| `milAdisc` | FLOAT64 | SUM of `curated_mil.milAdisc`: the document-level discount allocated to the lines; the salesperson share is already applied on ag01 split-sale lines. |
| `milCog` | FLOAT64 | SUM of `curated_mil.milCog`: gross line amount excluding VAT; the salesperson share is already applied on ag01 split-sale lines. |
| `milDisca` | FLOAT64 | SUM of `curated_mil.milDisca`: line discount amount excluding VAT; the salesperson share is already applied on ag01 split-sale lines. |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, the line net amount in THB; the salesperson share is already applied on ag01 split-sale lines. |
| `asatdate` | DATE | Build date, CURRENT_DATE('Asia/Bangkok'); the partition column. |

# How it is built

- Definition: `definitions/fact/fact_invoice.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactInvoiceSK`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["FactInvoiceSK"]}`.
- Reads: [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_company](/dimension/dim_company.md), [fact_table.fact_order](/fact/fact_order.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactInvoiceSK`, partition `asatdate`), after `dim_invoice`, `dim_customer`, `dim_company` and `fact_order`; row keys stay stable across rebuilds.

# Examples

Invoiced amount per month and type for one company.
```sql
SELECT DATE_TRUNC(mix_date, MONTH) AS month, milType, SUM(milSum) AS amount
FROM `databuffet-nonprd.fact_table.fact_invoice`
WHERE companyID = 'ag01' AND mix_date >= DATE '2026-01-01'
GROUP BY month, milType ORDER BY month, milType;
```
Invoice lines with no linked order.
```sql
SELECT milvnos, milStk, milSum
FROM `databuffet-nonprd.fact_table.fact_invoice`
WHERE milType = 'IS' AND OrderSK IS NULL AND mix_date >= DATE '2026-10-01';
```

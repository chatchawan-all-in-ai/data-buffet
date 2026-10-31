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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Invoice-line fact: lines of IS, BS, AS and QS documents from `curated_mil`, joined to `view_dim_invoice` for InvoiceSK, to the originating order line ([fact_order](/fact/fact_order.md), de-duplicated), the quotation, customer and company. It answers what was invoiced/billed and how it ties back to the order and quotation. Consumed by `view_fact_transcation`.

Used by / context: used by [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row per `FactInvoiceSK` (ROW_NUMBER over CompanySK, milYear, milMonth, milDay, milType, milVnos, milCus, LOWER(milStk)). Business grain: company + date + milType + `milvnos` + customer + product + `milLinkVcno` (the group-by includes `milLinkVcno`; the SK ORDER BY does not). Window: `mix_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR)`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactInvoiceSK` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, date, milType, milVnos, milCus, LOWER(milStk). Regenerates daily. |
| `InvoiceSK` | INT64 | Surrogate key from `view_dim_invoice` (join on date, type, vnos, customer, milLinkVcno, company). |
| `OrderSK` | INT64 | OrderSK of the linked order line from [fact_order](/fact/fact_order.md); NULL if none. |
| `FactOrderSK` | INT64 | [fact_order](/fact/fact_order.md).FactOrderSk of the linked order line. |
| `QuotationSK` | INT64 | QuotationSK inherited via fact_order. |
| `FactQuotationSK` | INT64 | FactQuotationSK inherited via fact_order ([fact_quotation](/fact/fact_quotation.md)). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md). |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code. |
| `mix_date` | DATE | Business date of the invoice (PARSE_DATE of year/month/day). |
| `milYear` | INT64 | Year of the document (curated_mil). |
| `milMonth` | INT64 | Month of the document (curated_mil). |
| `milDay` | INT64 | Day of the document (curated_mil). |
| `milType` | STRING | Document type: IS, BS, AS or QS. |
| `milvnos` | STRING | Invoice document number. |
| `milCus` | STRING | Customer code. |
| `milStk` | STRING | Product code on the line. |
| `milLinkVcno` | STRING | Link document number from curated_mil; part of the join to view_dim_invoice (NULL treated as ''). Exact business meaning not documented here (likely the linked order/original document, inferred from the name). |
| `milQuan` | FLOAT64 | Quantity: SUM of `curated_mil.milQuan` over the grain. |
| `milAdisc` | FLOAT64 | SUM of `curated_mil.milAdisc` (additional/line discount amount; exact meaning not documented in the repo, inferred from the name). |
| `milCog` | FLOAT64 | SUM of `curated_mil.milCog`: gross line amount excluding VAT, with salesperson shares already applied to split-sale lines. |
| `milDisca` | FLOAT64 | SUM of `curated_mil.milDisca` (discount amount; inferred from the name). |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, the line net amount in THB (a `milSum = 0` line is treated as free-of-charge in the store facts). |
| `asatdate` | DATE | Build date, CURRENT_DATE('Asia/Bangkok'); the partition column. |

# How it is built

- Definition: `definitions/fact/fact_invoice.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactInvoiceSK`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["FactInvoiceSK"]}`.
- Reads: [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_company](/dimension/dim_company.md), [fact_table.fact_order](/fact/fact_order.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactInvoiceSK`, partition `asatdate`), after `dim_invoice`, `dim_customer`, `dim_company` and `fact_order`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,485,005 rows, 457.1 MB.

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

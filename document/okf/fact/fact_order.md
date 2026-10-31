---
type: BigQuery Table
title: "fact_order"
description: "PS order aggregates expanded by retained product versions and matching quotation rows; quantities and amounts can repeat within a company/order/product."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_order&page=table"
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_order.sqlx"
    title: "Dataform definition (fact/fact_order.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Order-line fact: every product line of every PS (sales order) document in MAC5, joined to [dim_order](/dimension/dim_order.md) (INNER JOIN, so only orders present in dim_order appear), product, customer, company and the quotation line ([fact_quotation](/fact/fact_quotation.md)) it came from. It answers what was ordered, how much, at what value. Consumers: [fact_invoice](/fact/fact_invoice.md) (links invoices back to orders) and `view_fact_transcation`.

Used by / context: used by [fact_table.fact_invoice](/fact/fact_invoice.md), [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row per `FactOrderSk` (ROW_NUMBER over CompanySK, milYear, milMonth, milDay, milType, milVnos, milCus, lower(milStk)). Business grain: company + order date + milType ('PS') + order number (`milvnos`) + customer + product code. `curated_mil` lines are summed (GROUP BY 12 keys incl. ProductSK, OrderSK, mihRef1). ProductSK is part of the grouping: company/code matches to retained barcode versions each receive the same source totals. The subsequent quotation join can repeat each grouped row again for every matching Running + StkCode + CompanySK. FactOrderSk identifies these expanded candidates, not a unique business-line total. No date retention filter (4-year filter is commented out).

# Schema

| Column | Type | Description |
|---|---|---|
| `FactOrderSk` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, date, milType, milVnos, milCus, lower(milStk). Regenerates daily. |
| `OrderSK` | INT64 | Surrogate key of [dim_order](/dimension/dim_order.md) (join on date, type, vnos, customer, company). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md), joined on company and `lower(milStk) = lower(ProductCode)`; NULL if unmatched. |
| `QuotationSK` | INT64 | Surrogate key of dim_quotation carried from [fact_quotation](/fact/fact_quotation.md); NULL when no quotation line matches. |
| `FactQuotationSK` | INT64 | [fact_quotation](/fact/fact_quotation.md).FactQuotationSK of the matching quotation line (join `mihRef1 = Running`, `milStk = StkCode`, CompanySK). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`milCus = debcode`, same CompanySK). |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code (ag01, aa05, ab01, ac02, ak02). |
| `mix_date` | DATE | Business date of the order: PARSE_DATE of milYear, milMonth, milDay. |
| `milYear` | INT64 | Year of the order document (from curated_mil). |
| `milMonth` | INT64 | Month of the order document (from curated_mil). |
| `milDay` | INT64 | Day of the order document (from curated_mil). |
| `milType` | STRING | Document type; always 'PS' (sales order) here. |
| `milvnos` | STRING | Order document number; matches `dim_order.mihVnos`. |
| `milStk` | STRING | Product code on the line (case may vary). |
| `milCus` | STRING | Customer code (matches `dim_customer.debcode`). |
| `milQuan` | FLOAT64 | Quantity: SUM of `curated_mil.milQuan` over the grain. |
| `milAdisc` | FLOAT64 | SUM of `curated_mil.milAdisc` (additional/line discount amount; exact meaning not documented in the repo, inferred from the name). |
| `milCog` | FLOAT64 | SUM of `curated_mil.milCog`: gross line amount excluding VAT, with salesperson shares already applied to split-sale lines. |
| `milDisca` | FLOAT64 | SUM of `curated_mil.milDisca` (discount amount; inferred from the name). |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, the line net amount in THB (a `milSum = 0` line is treated as free-of-charge in the store facts). |
| `asatdate` | DATE | Build date: CURRENT_DATE('Asia/Bangkok') at the run; the partition column. |

# How it is built

- Definition: `definitions/fact/fact_order.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactOrderSk`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["FactOrderSk"]}`.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_order](/dimension/dim_order.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [fact_table.fact_quotation](/fact/fact_quotation.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactOrderSk`, partition `asatdate`, cluster `FactOrderSk`), after `dim_order`, `dim_customer`, `dim_product_master`, `dim_company` and `fact_quotation`. `FactOrderSk` regenerates daily; `fact_invoice` and `view_fact_transcation` rebuild after it.
- Approximate size (BigQuery metadata, 2026-10-31): 2,746,136 rows, 451.0 MB.

# Examples

Ordered source quantity and value per month before product/quotation enrichment, for PS lines with a matching order header.
```sql
SELECT DATE_TRUNC(DATE(m.milYear, m.milMonth, m.milDay), MONTH) AS month,
       SUM(m.milQuan) AS qty, SUM(m.milSum) AS amount
FROM `databuffet-nonprd.curated_mac5.curated_mil` AS m
WHERE m.company_id = 'ag01' AND m.milType = 'PS'
  AND DATE(m.milYear, m.milMonth, m.milDay) >= DATE '2026-01-01'
  AND EXISTS (
    SELECT 1 FROM `databuffet-nonprd.dimension_table.dim_order` AS o
    WHERE o.companyID = m.company_id AND o.mihType = m.milType
      AND o.mihVnos = m.milVnos AND o.mihCus = m.milCus
      AND o.mihYear = m.milYear AND o.mihMonth = m.milMonth AND o.mihDay = m.milDay
  )
GROUP BY month ORDER BY month;
```
Expanded order/quotation candidates for inspection; repeated amounts are not separate orders.
```sql
SELECT FactOrderSk, ProductSK, FactQuotationSK, milvnos, milStk, QuotationSK, milSum
FROM `databuffet-nonprd.fact_table.fact_order`
WHERE QuotationSK IS NOT NULL AND mix_date >= DATE '2026-10-01';
```

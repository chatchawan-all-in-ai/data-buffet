---
type: BigQuery Table
title: "fact_order"
description: "One row = the summed lines of one product on one PS sales order (company, date, order number, customer) per matched ProductSK and quotation line; quotation matches can repeat the quantities and amounts."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_order&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_order
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_order.sqlx"
    title: "Dataform definition (fact/fact_order.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-11T18:33:42+07:00" }
status: draft
---

# What it is

Order-line fact: every product line of every PS (sales order) document in MAC5, joined to [dim_order](/dimension/dim_order.md) (INNER JOIN, so only orders present in dim_order appear), product, customer, company and the quotation line ([fact_quotation](/fact/fact_quotation.md)) it came from. It answers what was ordered, how much, at what value.

Read by: [fact_invoice](/fact/fact_invoice.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [export_fact_order](/view/pub_sub/export_fact_order.md).

# Grain and key

One row = the summed lines of one product on one PS sales order (company, order date, `milvnos`, customer) per matched ProductSK and quotation line: key `FactOrderSk`. Its stable value is a typed business-key hash over company, order date, type, order number, customer, lower-case stock code and `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). `curated_mil` lines are summed (GROUP BY 12 keys incl. ProductSK, OrderSK, mihRef1). ProductSK is part of the grouping; the dimension grain is owned by the [product card](/dimension/dim_product_master.md#grain-and-key). The subsequent quotation join can repeat each grouped row again for every matching Running + StkCode + CompanySK. FactOrderSk identifies these expanded candidates, not a unique business-line total. No date retention filter.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactOrderSk` | INT64 | Stable row key: FARM_FINGERPRINT of typed company/date/type/order/customer/stock fields plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). Assigned in post_operations so the base aggregation order and FLOAT values stay unchanged. |
| `OrderSK` | INT64 | Surrogate key of [dim_order](/dimension/dim_order.md) (join on date, type, vnos, customer, company). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md), joined on company and `lower(milStk) = lower(ProductCode)`; NULL if unmatched. |
| `QuotationSK` | INT64 | Surrogate key of dim_quotation carried from [fact_quotation](/fact/fact_quotation.md); NULL when no quotation line matches. |
| `FactQuotationSK` | INT64 | [fact_quotation](/fact/fact_quotation.md).FactQuotationSK of the matching quotation line (join `mihRef1 = Running`, `milStk = StkCode`, CompanySK). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`milCus = debcode`, same CompanySK). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code (ag01, aa05, ab01, ac02, ak02). |
| `mix_date` | DATE | Business date of the order: PARSE_DATE of milYear, milMonth, milDay. |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milMonth` | INT64 | Month part of the document date. |
| `milDay` | INT64 | Day part of the document date. |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milvnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `milQuan` | FLOAT64 | SUM of `curated_mil.milQuan` over the grain; the salesperson share is already applied on ag01 split-sale lines. |
| `milAdisc` | FLOAT64 | SUM of `curated_mil.milAdisc`: the document-level discount allocated to the lines; the salesperson share is already applied on ag01 split-sale lines. |
| `milCog` | FLOAT64 | SUM of `curated_mil.milCog`: gross line amount excluding VAT; the salesperson share is already applied on ag01 split-sale lines. |
| `milDisca` | FLOAT64 | SUM of `curated_mil.milDisca`: line discount amount excluding VAT; the salesperson share is already applied on ag01 split-sale lines. |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, the line net amount in THB; the salesperson share is already applied on ag01 split-sale lines. |
| `asatdate` | DATE | Build date: CURRENT_DATE('Asia/Bangkok') at the run; the partition column. |

# How it is built

- Definition: `definitions/fact/fact_order.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactOrderSk`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["FactOrderSk"]}`.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_order](/dimension/dim_order.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [fact_table.fact_quotation](/fact/fact_quotation.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactOrderSk`, partition `asatdate`, cluster `FactOrderSk`), after `dim_order`, `dim_customer`, `dim_product_master`, `dim_company` and `fact_quotation`. The row key stays stable across rebuilds; `fact_invoice` and `view_fact_transcation` rebuild after it.

# Examples

Ordered quantity and value per month, counting each order line once (product-version and quotation matches repeat the source totals).
```sql
WITH order_lines AS (
  SELECT mix_date, milQuan, milSum
  FROM `databuffet-nonprd.fact_table.fact_order`
  WHERE companyID = 'ag01' AND mix_date >= DATE '2026-01-01'
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY CompanySK, OrderSK, milYear, milMonth, milDay, milType, milvnos, milCus, milStk
    ORDER BY FactOrderSk) = 1
)
SELECT DATE_TRUNC(mix_date, MONTH) AS month, SUM(milQuan) AS qty, SUM(milSum) AS amount
FROM order_lines
GROUP BY month ORDER BY month;
```
Expanded order/quotation candidates for inspection; repeated amounts are not separate orders.
```sql
SELECT FactOrderSk, ProductSK, FactQuotationSK, milvnos, milStk, QuotationSK, milSum
FROM `databuffet-nonprd.fact_table.fact_order`
WHERE QuotationSK IS NOT NULL AND mix_date >= DATE '2026-10-01';
```

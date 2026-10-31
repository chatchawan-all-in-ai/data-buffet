---
type: BigQuery Table
title: "fact_transaction_delivery"
description: "IS invoice aggregates by customer, company, InvoiceSK and matched ProductSK; retained barcode versions can repeat invoiced measures."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_transaction_delivery&page=table"
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_transaction_delivery.sqlx"
    title: "Dataform definition (fact/fact_transaction_delivery.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Invoice-line base used by the delivery tracking fact: IS (invoice) lines from `curated_mil` joined to [dim_invoice](/dimension/dim_invoice.md) and [dim_product_master](/dimension/dim_product_master.md). It provides the invoiced quantities/amounts that [fact_delivery](/fact/fact_delivery.md) attaches to trip/delivery status rows. Unlike [fact_invoice](/fact/fact_invoice.md) it covers only milType 'IS' and has no order/quotation links.

Used by / context: used by [fact_table.fact_delivery](/fact/fact_delivery.md).

# Grain and key

One row per `FactTransDeliverySK` (ROW_NUMBER over CompanySK, milYear, milMonth, milDay, milType, milvnos, lower(milStk)). Business grain: company + date + `milvnos` + customer + product (group-by also includes InvoiceSK and ProductSK). The company + case-insensitive product-code join matches every retained barcode version; each ProductSK group repeats the source measures. FactTransDeliverySK is an expanded-row key, not a unique invoice/product total. Window: invoice date >= start of the year 4 years ago (Asia/Bangkok).

# Schema

| Column | Type | Description |
|---|---|---|
| `FactTransDeliverySK` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, date parts, milType, milvnos, lower(milStk). Regenerates every run. |
| `InvoiceSK` | INT64 | Surrogate key of [dim_invoice](/dimension/dim_invoice.md) (join on date, type, vnos, customer, company; only milType 'IS'). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (company + case-insensitive product code); NULL if unmatched. |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code from dim_company. |
| `mix_date` | DATE | Invoice business date (PARSE_DATE of year/month/day); partition column. |
| `company_id` | STRING | MAC5 company code from curated_mil (same value as companyID). |
| `milYear` | INT64 | Year of the invoice document. |
| `milMonth` | INT64 | Month of the invoice document. |
| `milDay` | INT64 | Day of the invoice document. |
| `milType` | STRING | Document type; always 'IS' (invoice). |
| `milvnos` | STRING | Invoice document number; matches `fact_delivery.documentID`. |
| `milCus` | STRING | Customer code. |
| `milStk` | STRING | Product code of the line. |
| `milQuan` | FLOAT64 | SUM of `curated_mil.milQuan` over the grain. |
| `milAdisc` | FLOAT64 | SUM of `curated_mil.milAdisc` (discount amount; inferred from the name). |
| `milCog` | FLOAT64 | SUM of `curated_mil.milCog`: gross line amount excluding VAT, with salesperson shares already applied to split-sale lines. |
| `milDisca` | FLOAT64 | SUM of `curated_mil.milDisca` (discount amount; inferred from the name). |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, line net amount in THB. |
| `asatdate` | DATE | Build date, CURRENT_DATE('Asia/Bangkok'). |

# How it is built

- Definition: `definitions/fact/fact_transaction_delivery.sqlx` (`type: "operations"`, tags `fact_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: full refresh each run (`type: "operations"`: `CREATE OR REPLACE TABLE ... PARTITION BY mix_date CLUSTER BY FactTransDeliverySK`), tag `fact_daily`, after `dim_invoice`, `dim_product_master`, `dim_company`; runs before `fact_delivery`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,499,203 rows, 391.6 MB.

# Examples

Invoiced source quantity and amount per month before product enrichment, for IS lines with a matching invoice header.
```sql
SELECT DATE_TRUNC(DATE(m.milYear, m.milMonth, m.milDay), MONTH) AS month,
       SUM(m.milQuan) AS qty, SUM(m.milSum) AS amount
FROM `databuffet-nonprd.curated_mac5.curated_mil` AS m
WHERE m.company_id = 'ag01' AND m.milType = 'IS'
  AND DATE(m.milYear, m.milMonth, m.milDay) >= DATE '2026-01-01'
  AND EXISTS (
    SELECT 1 FROM `databuffet-nonprd.dimension_table.dim_invoice` AS i
    WHERE i.companyID = m.company_id AND i.mihType = m.milType
      AND i.mihVnos = m.milVnos AND i.mihCus = m.milCus
      AND i.mihYear = m.milYear AND i.mihMonth = m.milMonth AND i.mihDay = m.milDay
  )
GROUP BY month ORDER BY month;
```
Expanded invoice/product-version rows for inspection; measures can repeat.
```sql
SELECT FactTransDeliverySK, InvoiceSK, ProductSK, milStk, milQuan, milSum
FROM `databuffet-nonprd.fact_table.fact_transaction_delivery`
WHERE milvnos = '<invoice no>' AND companyID = 'ag01';
```

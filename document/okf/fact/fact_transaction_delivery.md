---
type: BigQuery Table
title: "fact_transaction_delivery"
description: "One row = the invoiced totals of one product on one IS invoice (company, date, invoice number, customer) per matched ProductSK, for the last four years; retained barcode versions repeat the measures."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_transaction_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_transaction_delivery
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_transaction_delivery.sqlx"
    title: "Dataform definition (fact/fact_transaction_delivery.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Invoice-line base used by the delivery tracking fact: IS (invoice) lines from `curated_mil` joined to [dim_invoice](/dimension/dim_invoice.md) and [dim_product_master](/dimension/dim_product_master.md). It provides the invoiced quantities/amounts that [fact_delivery](/fact/fact_delivery.md) attaches to trip/delivery status rows. Unlike [fact_invoice](/fact/fact_invoice.md) it covers only milType 'IS' and has no order/quotation links.

Read by: [fact_delivery](/fact/fact_delivery.md), [export_fact_transaction_delivery](/view/pub_sub/export_fact_transaction_delivery.md).

# Grain and key

One row = the invoiced totals of one product on one IS invoice (company, date, `milvnos`, customer) per matched ProductSK: key `FactTransDeliverySK` (see [Schema](#schema) for key generation); the group-by also includes InvoiceSK and ProductSK. The INNER JOIN to `dim_invoice` drops lines without a matching invoice; the invoice join matches every InvoiceSK for the same company, date, type, invoice number and customer, regardless of linked order. The company + case-insensitive product-code join matches every retained barcode version; each InvoiceSK/ProductSK group repeats the source measures. FactTransDeliverySK is an expanded-row key, not a unique invoice/product total. Window: invoice date >= start of the year 4 years ago (Asia/Bangkok).

# Schema

| Column | Type | Description |
|---|---|---|
| `FactTransDeliverySK` | INT64 | Stable row key: FARM_FINGERPRINT of the company/date/type/document/lower-case-stock plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). |
| `InvoiceSK` | INT64 | Surrogate key of [dim_invoice](/dimension/dim_invoice.md) (join on date, type, vnos, customer, company; only milType 'IS'). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (company + case-insensitive product code); NULL if unmatched. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code from dim_company. |
| `mix_date` | DATE | Invoice business date (PARSE_DATE of year/month/day); partition column. |
| `company_id` | STRING | MAC5 company code from curated_mil (same value as companyID). |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milMonth` | INT64 | Month part of the document date. |
| `milDay` | INT64 | Day part of the document date. |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milvnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milQuan` | FLOAT64 | SUM of `curated_mil.milQuan` over the grain; the salesperson share is already applied on ag01 split-sale lines. |
| `milAdisc` | FLOAT64 | SUM of `curated_mil.milAdisc`: the document-level discount allocated to the lines; the salesperson share is already applied on ag01 split-sale lines. |
| `milCog` | FLOAT64 | SUM of `curated_mil.milCog`: gross line amount excluding VAT; the salesperson share is already applied on ag01 split-sale lines. |
| `milDisca` | FLOAT64 | SUM of `curated_mil.milDisca`: line discount amount excluding VAT; the salesperson share is already applied on ag01 split-sale lines. |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, line net amount in THB; the salesperson share is already applied on ag01 split-sale lines. |
| `asatdate` | DATE | Build date, CURRENT_DATE('Asia/Bangkok'). |

# How it is built

- Definition: `definitions/fact/fact_transaction_delivery.sqlx` (`type: "operations"`, tags `fact_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: full refresh each run (`type: "operations"`: `CREATE OR REPLACE TABLE ... PARTITION BY mix_date CLUSTER BY FactTransDeliverySK`), tag `fact_daily`, after `dim_invoice`, `dim_product_master`, `dim_company`; runs before `fact_delivery`.

# Examples

Invoiced quantity and amount per month, counting each invoice line once (invoice candidates and product-version rows repeat the source measures).
```sql
WITH invoice_lines AS (
  SELECT mix_date, milQuan, milSum
  FROM `databuffet-nonprd.fact_table.fact_transaction_delivery`
  WHERE companyID = 'ag01' AND mix_date >= DATE '2026-01-01'
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY CompanySK, milYear, milMonth, milDay, milType, milvnos, milCus, milStk
    ORDER BY FactTransDeliverySK) = 1
)
SELECT DATE_TRUNC(mix_date, MONTH) AS month, SUM(milQuan) AS qty, SUM(milSum) AS amount
FROM invoice_lines
GROUP BY month ORDER BY month;
```
Expanded invoice-candidate/product-version rows for inspection; measures can repeat.
```sql
SELECT FactTransDeliverySK, InvoiceSK, ProductSK, milStk, milQuan, milSum
FROM `databuffet-nonprd.fact_table.fact_transaction_delivery`
WHERE milvnos = '<invoice no>' AND companyID = 'ag01';
```

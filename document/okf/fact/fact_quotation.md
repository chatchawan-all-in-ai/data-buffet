---
type: BigQuery Table
title: "fact_quotation"
description: "One row = the quoted totals of one stock code on one quotation (company, Running, customer, project) per matched ProductSK; retained barcode versions repeat the quoted quantities and totals."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_quotation&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_quotation
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_quotation.sqlx"
    title: "Dataform definition (fact/fact_quotation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Quotation-line fact: MAC5 quotation details (`validated_mac5.tbook_quodetail`) joined to [dim_quotation](/dimension/dim_quotation.md), product, customer and company. It answers what was quoted, at what average price, quantity and total. [fact_order](/fact/fact_order.md) joins it to attach the quotation behind an order line.

Read by: [fact_order](/fact/fact_order.md), [export_fact_quotation](/view/pub_sub/export_fact_quotation.md).

# Grain and key

One row = the quoted totals of one stock code on one quotation (company, `Running`, customer, project) per matched ProductSK: key `FactQuotationSK` (see [Schema](#schema) for key generation). The INNER JOIN to `dim_quotation` drops detail rows without a matching quotation. The detail is grouped by ProductSK, CompanySK, QuotationSK, SDate, Year/Month/Day, Running, StkCode, CustomerId, ProjectCode; `Price` is AVG, `Quantity`/`Total` are SUM, `StkDesc` is MAX. The product join uses company + stock code and retains each matching ProductSK, so the same source quantities and totals repeat across barcode versions. FactQuotationSK identifies an expanded row, not a unique quotation/product total.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactQuotationSK` | INT64 | Stable row key: FARM_FINGERPRINT of the typed company/quote-date/running/stock/customer/project grain plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). |
| `QuotationSK` | INT64 | Surrogate key of [dim_quotation](/dimension/dim_quotation.md) (join `dim_quotation.id = tbook_quodetail.linkid`, same company). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (`stkcode = ProductCode`, company). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`CustomerId = debcode`, company). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code. |
| `SDate` | DATE | Quotation date from dim_quotation (`SDate`). |
| `Year` | INT64 | Year of the quotation (from dim_quotation). |
| `Month` | INT64 | Month of the quotation (from dim_quotation). |
| `Day` | INT64 | Day of the quotation (from dim_quotation). |
| `Running` | STRING | Quotation running number (document number); equals `curated_mih.mihRef1` on linked orders (join in fact_order). |
| `StkCode` | STRING | Product code on the quotation line (`tbook_quodetail.stkcode`). |
| `CustomerId` | STRING | Customer code of the quotation (matches `dim_customer.debcode`). |
| `ProjectCode` | INT64 | Numeric project code parsed from the quotation Project text in dim_quotation; joins dim_project.projectCode. |
| `StkDesc` | STRING | Product description: MAX(stkdesc) over the group. |
| `Price` | FLOAT64 | Unit price: AVG(price) over the group. |
| `Quantity` | FLOAT64 | Quoted quantity: SUM(quantity). |
| `Total` | FLOAT64 | Quoted line total: SUM(total). |
| `asatdate` | DATE | Build date, CURRENT_DATE('Asia/Bangkok'); partition column. |

# How it is built

- Definition: `definitions/fact/fact_quotation.sqlx` (`type: "operations"`, tags `fact_daily`); the operation owns this table.
- Reads: [validated_mac5.tbook_quodetail](/validated/validated_mac5/tbook_quodetail.md), [dimension_table.dim_quotation](/dimension/dim_quotation.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: full refresh each run (`type: "operations"`: DROP then `CREATE OR REPLACE TABLE ... PARTITION BY asatdate CLUSTER BY FactQuotationSK`), tag `fact_daily`, after `dim_quotation`, `dim_customer`, `dim_product_master`, `dim_company`; runs before `fact_order`.

# Examples

Quoted value per month, counting each quotation line once (product-version rows repeat the source totals).
```sql
WITH quotation_lines AS (
  SELECT SDate, Total
  FROM `databuffet-nonprd.fact_table.fact_quotation`
  WHERE companyID = 'ag01' AND SDate >= DATE '2026-01-01'
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY CompanySK, QuotationSK, SDate, Running, StkCode, CustomerId, ProjectCode
    ORDER BY FactQuotationSK) = 1
)
SELECT DATE_TRUNC(SDate, MONTH) AS month, SUM(Total) AS quoted
FROM quotation_lines
GROUP BY month ORDER BY month;
```
Expanded product-version rows of one quotation; quantities and totals can repeat.
```sql
SELECT FactQuotationSK, ProductSK, Running, StkCode, StkDesc, Price, Quantity, Total
FROM `databuffet-nonprd.fact_table.fact_quotation`
WHERE Running = '<quotation running no>' AND companyID = 'ag01';
```

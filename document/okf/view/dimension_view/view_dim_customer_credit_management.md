---
type: BigQuery View
title: "view_dim_customer_credit_management"
description: "One row = one customer (CustomerSK) with credit terms/limit and its latest invoice and due credit-management grades."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_customer_credit_management&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_customer_credit_management
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_customer_credit_management.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_customer_credit_management.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Credit-management view: a narrow slice of [dim_customer](/dimension/dim_customer.md) (credit limit, credit term, memo) joined with the latest grade row of [dim_customer_grade](/dimension/dim_customer_grade.md), exposing the invoice-based and due-based grades. No other repo object reads it.

# Grain and key

One row = one customer: key `CustomerSK`. dim_customer_grade is reduced to one row per CustomerSK (highest CustomerGradeSK wins) before the LEFT JOIN, so customers without a grade have NULL grade columns.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerGradeSK` | INT64 | SK of the selected (highest) grade row in dim_customer_grade; NULL when the customer has no grade row. |
| `CustomerSK` | INT64 | Stable SK of the customer in dim_customer. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `debcode` | STRING | Customer (debtor) code. |
| `deblimit` | FLOAT64 | Credit limit of the customer in baht. |
| `debcreditterm` | INT64 | Credit term in days. |
| `debmemo` | STRING | Free-text memo on the customer. |
| `Invoice_Customer_CM_Grade` | STRING | Credit-management grade based on invoicing behaviour (`InvoiceGrade` in dim_customer_grade). |
| `Due_Customer_CM_Grade` | STRING | Credit-management grade based on due/overdue behaviour (`DueGrade` in dim_customer_grade). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_customer_credit_management.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md).

# Examples

Customers that have a due grade:

```sql
SELECT companyID, debcode, deblimit, debcreditterm, Invoice_Customer_CM_Grade, Due_Customer_CM_Grade
FROM `databuffet-nonprd.dimension_view.view_dim_customer_credit_management`
WHERE Due_Customer_CM_Grade IS NOT NULL
LIMIT 100
```

Customers per invoice grade:

```sql
SELECT Invoice_Customer_CM_Grade, COUNT(*) AS customers
FROM `databuffet-nonprd.dimension_view.view_dim_customer_credit_management`
GROUP BY Invoice_Customer_CM_Grade
ORDER BY Invoice_Customer_CM_Grade
```

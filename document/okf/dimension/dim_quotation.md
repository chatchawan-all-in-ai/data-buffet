---
type: BigQuery Table
title: "dim_quotation"
description: "One row = one MAC5 quotation (book quotation, identified by its running number) per company with date, project link, customer code, terms and a derived order-fulfilment status."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_quotation&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_quotation
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_quotation.sqlx"
    title: "Dataform definition (dimension/dim_quotation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Quotation dimension built from the curated MAC5 quotation book (`curated_tbook_quotation`). For each quotation it parses a customer code (`CustomerID`) and a numeric project code out of the free-text `Atten` and `Project` fields (backslash-separated), links to [dim_project](/dimension/dim_project.md), and computes `OrderStatus` by comparing quoted items/amounts (`tbook_quodetail`) with sales orders (PS) whose `mihRef1` is the quotation's running number and that contain the quoted stock code. It is the source of `QuotationSK` for [fact_quotation](/fact/fact_quotation.md).

Read by: [export_dim_quotation](/view/pub_sub/export_dim_quotation.md), [fact_quotation](/fact/fact_quotation.md).

# Grain and key

One row = one MAC5 quotation: key (`CompanySK`, `Running`), where `Running` is the quotation running number. `QuotationSK` is a stable surrogate key (existing quotations keep it; new ones get `max_sk + ROW_NUMBER()` ordered by `CompanySK`, `Running`). `ID` is the source row id.

# Schema

| Column | Type | Description |
|---|---|---|
| `QuotationSK` | INT64 | Stable surrogate key; never regenerated, stored in [fact_quotation](/fact/fact_quotation.md). |
| `ProjectSK` | INT64 | Project SK from [dim_project](/dimension/dim_project.md), joined on parsed `ProjectCode` and `CompanySK`; NULL when no project code was parsed or found. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code. |
| `ID` | INT64 | Quotation identifier, referenced by `tbook_quodetail.linkid`. |
| `Running` | STRING | Quotation number referenced by orders, with missing source numbers represented as an empty string. |
| `SDate` | DATE | Quotation date. |
| `Year` | INT64 | Year of `SDate`. |
| `Month` | INT64 | Month of `SDate`. |
| `Day` | INT64 | Day of `SDate`. |
| `Atten` | STRING | Attention or contact text of the quotation, including a customer code before a backslash when supplied. |
| `Project` | STRING | Project text of the quotation, including a project or customer code before a backslash when supplied. |
| `UInsert` | STRING | Employee code of the user who created the row. |
| `PriceValidity` | STRING | Price validity text. |
| `TermDelivery` | STRING | Delivery terms text. |
| `TermPayment` | STRING | Payment terms text (e.g. credit 30 days). |
| `CustomerID` | STRING | Customer code parsed from `Atten` (alphanumeric, 5+ characters before a backslash) or, failing that, from `Project` (alphanumeric, 7+ characters); NULL if none. |
| `ProjectCode` | INT64 | Numeric project code (2+ digits) parsed from the first part of `Project`; NULL when that part was taken as a customer code or is not numeric. |
| `OrderStatus` | STRING | Fulfilment status: per quoted item 'On Order' (no PS order line for that stock code with `mihRef1 = Running`), 'Complete' (ordered quantity and amount >= quoted), else 'In Process'; per quotation any 'In Process' wins, then 'On Order', else 'Complete'. NULL when the quotation has no detail lines. |

# How it is built

- Definition: `definitions/dimension/dim_quotation.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_tbook_quotation](/curated/curated_mac5/curated_tbook_quotation.md), [validated_mac5.tbook_quodetail](/validated/validated_mac5/tbook_quodetail.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_project](/dimension/dim_project.md).
- MERGE with stable SK (`type: "operations"`, tag `dimension_daily`); the existing SK is looked up by `Running` + `CompanySK`; updates the attribute columns, inserts new quotations, no delete. Reads the whole curated quotation table each run (no window); runs after dim_company and dim_project.

# Examples

Quotations per company and fulfilment status for the current year.

```sql
SELECT companyID, OrderStatus, COUNT(*) AS quotations
FROM `databuffet-nonprd.dimension_table.dim_quotation`
WHERE Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY companyID, OrderStatus
ORDER BY companyID, OrderStatus;
```

Quotations that parsed to a project and customer code.

```sql
SELECT companyID, Running, SDate, CustomerID, ProjectCode, ProjectSK
FROM `databuffet-nonprd.dimension_table.dim_quotation`
WHERE ProjectSK IS NOT NULL AND CustomerID IS NOT NULL
ORDER BY SDate DESC
LIMIT 50;
```

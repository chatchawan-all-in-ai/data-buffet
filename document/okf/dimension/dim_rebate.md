---
type: BigQuery Table
title: "dim_rebate"
description: "One row = one rebate or sales-KPI exclusion rule of a company: a code (rebate) of a given status type (customer, sales, product, dep, textsplit) with its sales and accounting exclusion flags, from the MDS KPI condition master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_rebate&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_rebate
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_rebate.sqlx"
    title: "Dataform definition (dimension/dim_rebate.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Rule list that decides which transaction lines are excluded from sales KPIs (`salesExc`) and accounting KPIs (`accExc`). `view_fact_transcation` matches every line against the rules by status and derives `FlagSaleExc` / `FlagAccExc`; `view_dim_product_master` joins the `Product` rules by product code for `FlagSalesExc` / `FlagAccExc` (default 'No').

Read by: [view_dim_product_master](/view/dimension_view/view_dim_product_master.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one active MDS rule row: key `RebateSK`, `ROW_NUMBER()` ordered by companyID, rebate, status; natural key `(companyID, rebate, status)` (uniqueness is not enforced). The meaning of `rebate` depends on `status`: status `cutomer` (sic) compares to the line customer `milCus`, `sales` to the sales person `milPer`, `product` to the product code `milStk`, `textsplit` is a substring matched against the line description, the product description or the department (view_fact_transcation). Rows with status `dep` (department `milDep`) are not applied: view_fact_transcation keeps only the `cutomer`, `sales`, `product` and `textsplit` statuses. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `RebateSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by companyID, rebate, status. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `rebate` | STRING | The code or text the rule matches; its meaning depends on `status` (customer code, sales person code, product code, department code, or a text fragment for textsplit). `view_fact_transcation` compares it after TRIM. |
| `rebateName` | STRING | Descriptive name of the rule, from MDS. |
| `status` | STRING | Rule type that tells which field `rebate` is compared to: `cutomer` (spelled this way), `sales`, `product`, `dep` (not applied by view_fact_transcation), `textsplit`. Consumers compare it case-insensitively with TRIM in view_fact_transcation; view_dim_product_master tests `status = 'Product'` exactly. |
| `type` | STRING | Name of the MAC5 field(s) the rebate rule matches on, e.g. `StkCode`, `MilPer`, `mildep`; several fields are joined by the pipe character (`MilCus`, `MihCus`). Not used by any definition in this repo. |
| `salesExc` | STRING | 'Yes' when matching lines are excluded from sales KPIs; consumers treat any other value as no exclusion (default 'No'). |
| `accExc` | STRING | 'Yes' when matching lines are excluded from accounting KPIs; any other value is no exclusion. |
| `MdsID` | STRING | `id` of the source row in `mds_data_sales_kpi_condition_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_rebate.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `RebateSK`.
- Storage options: `{"clusterBy": ["RebateSK"]}`.
- Reads: `mds_dataset.mds_data_sales_kpi_condition_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Product-level rebate rules that exclude lines from sales KPIs.

```sql
SELECT companyID, rebate, rebateName, salesExc, accExc
FROM `databuffet-nonprd.dimension_table.dim_rebate`
WHERE LOWER(TRIM(status)) = 'product' AND salesExc = 'Yes';
```

Rule count by status.

```sql
SELECT companyID, status, COUNT(*) AS rules
FROM `databuffet-nonprd.dimension_table.dim_rebate`
GROUP BY 1, 2 ORDER BY 1, 2;
```

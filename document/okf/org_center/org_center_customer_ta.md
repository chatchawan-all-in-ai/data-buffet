---
type: BigQuery Table
title: "org_center_customer_ta"
description: "One row = one customer in the portfolio of one TA department for a date range, from the MDS customer-to-TA portfolio master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_customer_ta&page=table"
project_id: databuffet-nonprd
dataset_id: org_center
table_id: org_center_customer_ta
tags: ["org_center", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_customer_ta.sqlx"
    title: "Dataform definition (org_center/org_center_customer_ta.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Customer portfolio of each TA department: which customer (by company and customer code) a department (the TA position) is responsible for, with the share of the customer and the date range. Rows mirror the active rows of the source listed under How it is built.

Read by: [rls_ta_customer](/process/rls_ta_customer.md), [org_center_flags](/org_center/org_center_flags.md), [export_customer_ta_assignments](/view/pub_sub/export_customer_ta_assignments.md).

# Grain and key

One row = one customer in the portfolio of one TA department for a date range: key `company_id` + `customer_code` + `department_id` + `valid_from` (the MDS key). `department_id` is NULL when DepartmentID is empty; such rows give access to nobody and are flagged NO_DEPARTMENT in [org_center_flags](/org_center/org_center_flags.md).

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (companyID), trimmed; empty becomes NULL. |
| `customer_code` | STRING | Customer code (CustomerCode), trimmed; empty becomes NULL. |
| `department_id` | STRING | TA department (DepartmentID) responsible for the customer, trimmed; empty becomes NULL. |
| `share_percent` | FLOAT64 | Share of the customer assigned to the department (SharePercent). |
| `valid_from` | DATE | StartDate of the assignment. |
| `valid_to` | DATE | EndDate of the assignment, EXCLUSIVE (the first day the department is no longer responsible); empty EndDate becomes 2066-12-31. |
| `customer_name` | STRING | Customer name as entered in MDS (CustomerName), trimmed; empty becomes NULL. |
| `source_row_id` | STRING | `id` of the MDS row, for tracing back to the portfolio source. |

# How it is built

- Definition: `definitions/org_center/org_center_customer_ta.sqlx`.
- `uniqueKey`: the four columns listed under Grain and key.
- Storage options: `{"clusterBy": ["company_id", "customer_code"]}`.
- Reads: `mds_dataset.mds_data_ta_customer` (master data loaded outside this repo), active rows only (`is_active = TRUE`).
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Depends on `org_center_schema`.

# Examples

Current customers of one TA department.

```sql
SELECT customer_code, customer_name, share_percent, valid_from, valid_to
FROM `databuffet-nonprd.org_center.org_center_customer_ta`
WHERE company_id = 'ag01'
  AND department_id = '<department id>'
  AND CURRENT_DATE('Asia/Bangkok') >= valid_from AND CURRENT_DATE('Asia/Bangkok') < valid_to
```

---
type: BigQuery Table
title: "rls_ta_customer"
description: "One row = one viewer (employee) x one customer (company + code, or ALL) x one product scope that the viewer may see today, expanded from the org center department portfolios, manager tree and special-access exceptions."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=rls_ta_customer&page=table"
project_id: databuffet-nonprd
dataset_id: process_dataset
table_id: rls_ta_customer
tags: ["process", "RLS", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/process/rls_ta_customer.sqlx"
    title: "Dataform definition (process/rls_ta_customer.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Precomputed "who sees which customer" table for the TA app and the AI Advisor. Marts are filtered by joining them to this table on the viewer's `employee_id`, the customer's company and code, and the product scope. It is built from [org_center_unit](/org_center/org_center_unit.md), [org_center_member](/org_center/org_center_member.md), [org_center_customer_ta](/org_center/org_center_customer_ta.md), [org_center_exception](/org_center/org_center_exception.md), [dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dim_section_last](/dimension/dim_section_last.md) and [dim_company](/dimension/dim_company.md). It is separate from [rls_customer360](/process/rls_customer360.md) (Power BI).

Read by: [export_rls_ta_customer](/view/pub_sub/export_rls_ta_customer.md).

# Grain and key

One row = one viewer x one customer x one product scope visible today: key `employee_id` + `customer_company_id` + `customer_code` + `marketing_group_id` + `sub_marketing_id` + `segment_id`, as of today (Asia/Bangkok). `customer_code = 'ALL'` means every customer of that company; `'ALL'` in a product column means no product restriction. No key column is NULL.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_id` | STRING | The viewer: MDS employee code (the TA app's `person_key`). |
| `customer_company_id` | STRING | Company of the customer and of the mart sales rows (for TA and manager rows also the company of the viewer's seat; for EXCEPTION rows a company in the exception's scope). |
| `customer_code` | STRING | ERP customer code, or `ALL` = every customer of `customer_company_id`. |
| `marketing_group_id` | STRING | `ALL` or a marketing group code (non-`ALL` only on special-access product rows). |
| `sub_marketing_id` | STRING | `ALL` or a marketing sub-group code. |
| `segment_id` | STRING | `ALL` or a segment code. |
| `access_source` | STRING | Where the access comes from: `TA` (portfolio customers, in the same company, of every department the viewer is seated in today as TA), `SECTION_MGR`, `REGION_MGR`, `DIRECTOR`, `CEO` (portfolio customers of every department with a TA seated today in a section under the viewer's unit) or `EXCEPTION` (special access). When several apply the first in this order is kept. |

# How it is built

- Definition: `definitions/process/rls_ta_customer.sqlx` (`type: "table"`, tag `dimension_daily`).
- `uniqueKey`: the six key columns listed under Grain and key.
- Storage options: `{"clusterBy": ["employee_id", "customer_company_id"]}`.
- Reads: [org_center.org_center_unit](/org_center/org_center_unit.md), [org_center.org_center_member](/org_center/org_center_member.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [org_center.org_center_customer_ta](/org_center/org_center_customer_ta.md), [org_center.org_center_exception](/org_center/org_center_exception.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Only rows valid today are used: units and members `BETWEEN valid_from AND valid_to`; portfolio rows `valid_from <= today < valid_to`.
- TA: the portfolio is bound to a department within the customer’s company. Today's TA seats come from the sale representative dimension (a TA is seated in a department between its start and end date; the section of the seat gives the unit). Every TA seated in a department today sees that department's portfolio customers in the same company, so two TAs in one department both see them. Portfolio rows with no `department_id` give access to nobody. Managers (SECTION_MGR, REGION_MGR, DIRECTOR, CEO): portfolio customers of every TA seated today in the sections under the manager's unit, walked through the fixed four-level tree (section, region, division, company). Co-managed customers appear for each TA in full (`share_percent` is not used).
- Exceptions (`org_center_exception`, rows without `employee_id` skipped): a whole-company exception (`flag_customer` false, or director, region and section all `ALL`) gives one row per company in scope with `customer_code = 'ALL'` (`company_code = 'ALL'` = every company in `dim_company`); a by-unit exception gives the portfolio customers in the exception's company scope of TAs in sections matching every non-`ALL` field (division `unit_code`, `org_center_unit.region_code`, section `unit_code`). Product columns come from the exception row.
- Full nightly rebuild; runs after the four `org_center_*` tables, `dim_sale_representative_last` and `dim_section_last`, the `update_sk_sale_rep_group` backfill, and `dim_company`.

# Examples

Mart rows visible to one viewer (company and customer code are always joined together). Use `EXISTS` so overlapping grants do not duplicate mart rows. If a mart lacks a product scope column, require `ALL` in that RLS column; do not omit the restriction.

```sql
SELECT m.*
FROM `databuffet-nonprd.<mart_dataset>.<mart_table>` AS m
WHERE EXISTS (
  SELECT 1
  FROM `databuffet-nonprd.process_dataset.rls_ta_customer` AS r
  WHERE r.employee_id = '<viewer employee code>'
    AND r.customer_company_id = m.company_source_id
    AND (r.customer_code = 'ALL' OR r.customer_code = m.customer_code)
    AND (r.marketing_group_id = 'ALL' OR r.marketing_group_id = m.marketing_group_id)
    AND (r.sub_marketing_id = 'ALL' OR r.sub_marketing_id = m.sub_marketing_id)
    AND (r.segment_id = 'ALL' OR r.segment_id = m.segment_id)
)
```

Customers of one viewer by source.

```sql
SELECT access_source, COUNT(*) AS rows_visible
FROM `databuffet-nonprd.process_dataset.rls_ta_customer`
WHERE employee_id = '<viewer employee code>'
GROUP BY access_source
```

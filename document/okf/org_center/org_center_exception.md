---
type: BigQuery Table
title: "org_center_exception"
description: "One row = one person x company x product scope of a special access exception, copied from the MDS special-RLS table with ALL for unrestricted values and the lists split."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_exception&page=table"
project_id: databuffet-nonprd
dataset_id: org_center
table_id: org_center_exception
tags: ["org_center", "mds", "dimension_daily", "org_center"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_exception.sqlx"
    title: "Dataform definition (org_center/org_center_exception.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Special access exceptions of the org center: which company, director, region, section and product scope (marketing group, sub group, segment) a person may see beyond the org chart. Active rows of `mds_dataset.mds_data_org_rls_special` are expanded into company and product scopes. The value 'ALL' means unrestricted. Rows without an employee code are kept (employee_id is NULL) and are reported by [org_center_flags](/org_center/org_center_flags.md).

Read by: [rls_ta_customer](/process/rls_ta_customer.md), [org_center_flags](/org_center/org_center_flags.md), [export_access_exceptions](/view/pub_sub/export_access_exceptions.md), [export_employees](/view/pub_sub/export_employees.md).

# Grain and key

One row = one person x company x product scope of a special access exception: key `source_row_id` (the MDS row id) + `company_code` + `marketing_group_id` + `sub_marketing_id` + `segment_id`. Company lists are split on '|' and cross-expanded independently of the product pairing, producing one company code per row. One MDS row expands to several product scopes when its marketing group, sub group or segment hold '|' lists: the three lists are paired by position (a missing position takes the first value of that list), the same pairing as `view_rls_special_data`. The `department` column of the MDS table is not used.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_id` | STRING | Employee code (employeeid); NULL when the MDS row has none. |
| `company_code` | STRING | One company code from companyreport split on '\|', trimmed; empty = 'ALL'. |
| `director_code` | `ARRAY<STRING>` | Director codes (director split on '\|', trimmed, empty items dropped, source order preserved); ['ALL'] when empty. |
| `region_code` | `ARRAY<STRING>` | Region codes (region split on '\|', normalized as director_code); ['ALL'] when empty. |
| `section_code` | `ARRAY<STRING>` | Section codes (section split on '\|', normalized as director_code); ['ALL'] when empty. |
| `marketing_group_id` | STRING | One marketing group code from mktgroupid; empty = 'ALL'. |
| `sub_marketing_id` | STRING | Marketing sub group paired by position with the group (mktsubgroupid); empty = 'ALL'. |
| `segment_id` | STRING | Marketing segment paired by position with the group (mktsegmentid); empty = 'ALL'. |
| `flag_customer` | BOOL | flagcustomer of the MDS row; NULL = FALSE. |
| `source_row_id` | STRING | id of the MDS row the row comes from. |

# How it is built

- Definition: `definitions/org_center/org_center_exception.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `source_row_id`, `company_code`, `marketing_group_id`, `sub_marketing_id`, `segment_id`.
- Storage options: `{"clusterBy": ["employee_id", "company_code"]}`.
- Reads: `mds_dataset.mds_data_org_rls_special` (master data loaded outside this repo), active rows only.
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Depends on `org_center_schema`.

# Examples

Exceptions of one person.

```sql
SELECT company_code, director_code, marketing_group_id, sub_marketing_id, segment_id, flag_customer
FROM `databuffet-nonprd.org_center.org_center_exception`
WHERE employee_id = '1045001'
```

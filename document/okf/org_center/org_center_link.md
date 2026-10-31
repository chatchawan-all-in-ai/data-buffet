---
type: BigQuery Table
title: "org_center_link"
description: "One row = one promoter (PC) linked to one TA at one branch for a date range, from the MDS PC-to-TA assignment table."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_link&page=table"
tags: ["org_center", "mds", "dimension_daily", "org_center"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_link.sqlx"
    title: "Dataform definition (org_center/org_center_link.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

PC-to-TA assignment table of the org center (the TA app's member_links with link_type 'PC_TA'): from = PC (promoter, employee type MDT or partner agent), to = TA, site = branch. Rows mirror mds_dataset.mds_data_pc_ta (active rows) as entered. [org_center_member](/org_center/org_center_member.md) uses it to create the PC_MDT and PC_AGENT member rows, and [org_center_flags](/org_center/org_center_flags.md) checks it. The table currently has 0 rows (the MDS source table is empty).

# Grain and key

One row per `company_id` + `pc_employee_id` + `branch_type` + `branch_code` + `valid_from` (the MDS key; the MDS team guarantees one valid row per (company, PC, branch type, branch) per day, so periods do not overlap). Values are passed through untouched: no trim, no case change, no filtering of unknown codes (wrong codes are fixed in MDS).

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (companyID of mds_data_pc_ta). |
| `link_type` | STRING | Constant 'PC_TA'. |
| `pc_employee_id` | STRING | PC employee code (PCEmployeeID). |
| `pc_type` | STRING | PC type from the active mds_data_mdt_sales_pc_master row (latest end_date, start_date, updated_at, lowest id): NULL or empty employee_type gives PC_MDT, 'พันธมิตร' gives PC_AGENT; any other value, or a PC missing from the active master, gives NULL. |
| `branch_code` | STRING | Branch code (BranchCode). |
| `branch_type` | STRING | Branch type (BranchType). |
| `ta_employee_id` | STRING | TA employee code (TAEmployeeID) responsible for the PC at that branch. |
| `valid_from` | DATE | StartDate of the assignment. |
| `valid_to` | DATE | EndDate of the assignment, EXCLUSIVE (the first day the TA is no longer responsible); empty EndDate becomes 2066-12-31. |
| `company_name` | STRING | dim_company.CompanyNameTH by company_id. |

# How it is built

- Definition: `definitions/org_center/org_center_link.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `company_id`, `pc_employee_id`, `branch_type`, `branch_code`, `valid_from`.
- Storage options: `{"clusterBy": ["company_id", "pc_employee_id"]}`.
- Reads: `mds_dataset.mds_data_mdt_sales_pc_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md), `mds_dataset.mds_data_pc_ta` (master data loaded outside this repo).
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Depends on `org_center_schema` and `dim_company`; reads mds_data_pc_ta and mds_data_mdt_sales_pc_master (master data loaded outside this repo). 0 rows while the MDS table is empty.
- Approximate size (BigQuery metadata, 2026-10-31): 0 rows, 0 B.

# Examples

Current PC assignments of one company.

```sql
SELECT pc_employee_id, pc_type, branch_code, ta_employee_id, valid_from, valid_to
FROM `databuffet-nonprd.org_center.org_center_link`
WHERE company_id = 'ag01'
  AND CURRENT_DATE('Asia/Bangkok') >= valid_from AND CURRENT_DATE('Asia/Bangkok') < valid_to
```

---
type: BigQuery Table
title: "org_center_member"
description: "One row = one person holding one position at one unit for a date range (CEO, director, region manager, section manager, TA, or PC)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_member&page=table"
tags: ["org_center", "mds", "dimension_daily", "org_center"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_member.sqlx"
    title: "Dataform definition (org_center/org_center_member.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Org-center membership table: who sits where. Positions are CEO (from `mds_data_company_master.CEOEmpID`, seated on the COMPANY unit `CO-<company_id>`), DIRECTOR, REGION_MGR, SECTION_MGR (from the dim_*_last tables), TA (sales representatives with a department, grouped by section) and PC_MDT / PC_AGENT (promoters linked to a TA via [org_center_link](/org_center/org_center_link.md)). It is the TA app's 'appointments' and the basis of [org_center_person](/org_center/org_center_person.md) (the who-is-who list); units are in [org_center_unit](/org_center/org_center_unit.md). Contact e-mails come from the MDS employee mapping table.

# Grain and key

One row per `company_id` + `employee_id` + `position_code` + `unit_id` + `valid_from` (the declared key). A TA whose departments sit in several sections gets one row per section, with `department_ids` listing the merged departments; PC rows merge overlapping or adjacent periods across branches and TAs into one contiguous interval per company, person, PC type and unit, while disjoint periods stay as separate rows. Rows with NULL `employee_id` are dropped.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code. |
| `employee_id` | STRING | MDS employee code (the TA app's person_key). For PC rows it is the link's pc_employee_id. |
| `first_name` | STRING | First name from the dim of that position (for DIRECTOR the DirectorOfSalesName split at the first word); for PCs from mds_data_mdt_sales_pc_master. |
| `last_name` | STRING | Surname from the same source (rest of the name for DIRECTOR). |
| `nickname` | STRING | Nickname from the dim; NULL for DIRECTOR and PC rows. |
| `email` | STRING | Email from mds_data_org_employee_mapping_center (active rows, a non-NULL email first, then latest updated_at); NULL when the person is not in that table. |
| `position_code` | STRING | CEO, DIRECTOR, REGION_MGR, SECTION_MGR, TA, PC_MDT or PC_AGENT. |
| `unit_id` | STRING | Unit held at (join to org_center_unit.unit_id for the same company): DIR-/REG-/SEC- keys. TA rows: the section of the TA's department; PC rows: the unit of the linked TA's overlapping TA row (disambiguated by the branch's zone_id when the TA has several units; no match means no member row). |
| `department_ids` | ARRAY<STRING> | TA departments merged into the row (ARRAY of department ids); empty for managers and PCs. |
| `valid_from` | DATE | Start of the inclusive membership interval (dim StartDate; for a TA the earliest start over merged departments; for PCs the overlap with the link period). |
| `valid_to` | DATE | End of the inclusive interval (dim EndDate; latest end for a TA; 2066-12-31 = still active; for PCs the link's exclusive valid_to minus one day unless 2066-12-31). |
| `company_name` | STRING | dim_company.CompanyNameTH by company_id. |

# How it is built

- Definition: `definitions/org_center/org_center_member.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `company_id`, `employee_id`, `position_code`, `unit_id`, `valid_from`.
- Storage options: `{"clusterBy": ["company_id", "employee_id"]}`.
- Reads: `mds_dataset.mds_data_org_employee_mapping_center` (master data loaded outside this repo), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), `mds_dataset.mds_data_mdt_sales_pc_master` (master data loaded outside this repo), [org_center.org_center_link](/org_center/org_center_link.md), `mds_dataset.mds_data_mdt_sales_branch_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md), `mds_dataset.mds_data_company_master` (master data loaded outside this repo).
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Runs after `update_sk_sale_rep_group`, `dim_company`, `org_center_link` and the dim_*_last tables (director, region manager, section manager, sale representative) and reads mds_data_org_employee_mapping_center, mds_data_mdt_sales_pc_master and mds_data_mdt_sales_branch_master.
- Approximate size (BigQuery metadata, 2026-10-31): 604 rows, 106.4 KB.

# Examples

Active members of one section with their position.

```sql
SELECT employee_id, position_code, unit_id, valid_from, valid_to
FROM `databuffet-nonprd.org_center.org_center_member`
WHERE company_id = 'ag01' AND unit_id = 'SEC-NE1'
  AND CURRENT_DATE('Asia/Bangkok') BETWEEN valid_from AND valid_to
```

Number of active members per position and company.

```sql
SELECT company_id, position_code, COUNT(DISTINCT employee_id) AS people
FROM `databuffet-nonprd.org_center.org_center_member`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN valid_from AND valid_to
GROUP BY company_id, position_code
ORDER BY company_id, position_code
```

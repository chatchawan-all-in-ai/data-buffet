---
type: BigQuery Table
title: "org_center_unit"
description: "One row = one organisation unit (company, division, region or section) of one company."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_unit&page=table"
tags: ["org_center", "dimension_daily", "org_center"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_unit.sqlx"
    title: "Dataform definition (org_center/org_center_unit.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Org-center table of organisational units for the TA AI Assistant: the four levels COMPANY (บริษัท, depth 0, from `mds_data_company_master`), DIVISION (ฝ่าย), REGION (ภาค) and SECTION (ส่วน, the TA app's 'team'), taken from dim_director_last, dim_region_last and dim_section_last. It is the 'where' side of the org center: [org_center_member](/org_center/org_center_member.md) says who sits in each unit, and [org_center_flags](/org_center/org_center_flags.md) reports data-quality problems against it. Intended base for Power BI RLS, the TA app and other access rules.

# Grain and key

One row per `company_id` + `unit_id` (`unit_id` = prefix `CO-`/`DIR-`/`REG-`/`SEC-` + code, e.g. CO-ag01, DIR-00001, REG-NE, SEC-NE1). COMPANY units have NULL `parent_unit_id`; divisions point to their `CO-<company_id>` unit; regions point to a division and sections to a region. Department (เขต) is not a level.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (companyID of the source dim). |
| `unit_id` | STRING | Unit key: `DIR-` / `REG-` / `SEC-` plus `unit_code`; the prefix prevents collisions across levels. |
| `unit_level` | STRING | COMPANY, DIVISION, REGION or SECTION. |
| `depth` | INT64 | 0 = COMPANY, 1 = DIVISION, 2 = REGION, 3 = SECTION. |
| `unit_code` | STRING | CompanyID (company; cleaned MDS value), DirectorID (division), SubRegionID (region; not RegionID, because region PS1 has five sub-regions PS1-1..PS1-5) or SectionID (section). |
| `unit_name` | STRING | CompanyNameTH (company, from MDS) / DirectorName / RegionName / SectionName of the source dim. |
| `parent_unit_id` | STRING | unit_id of the parent unit (region to division, section to region); NULL for a company; a division points to its company unit. |
| `valid_from` | DATE | StartDate of the latest `_last` dim row for the unit. |
| `valid_to` | DATE | EndDate of the `_last` dim row; 2066-12-31 means still active. |
| `plan_code` | STRING | The unit's code in the org plan file Org_Mock_Master_Plan_v4.xlsx: DIVISION = DirectorID; REGION = RegionID (the five PS1-n sub-regions all map to PS1); SECTION = unit_code except 7 dummy sections named by a fixed list in the SQL (e.g. Dummy999994 to HO, Dummy999993 to Imboon, Dummy999991 to Online). |
| `company_name` | STRING | dim_company.CompanyNameTH by company_id; NULL if the company is not in the dim. |

# How it is built

- Definition: `definitions/org_center/org_center_unit.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `company_id`, `unit_id`.
- Storage options: `{"clusterBy": ["company_id", "unit_id"]}`.
- Reads: [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_company](/dimension/dim_company.md), `mds_dataset.mds_data_company_master` (master data loaded outside this repo).
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Runs after `update_sk_sale_rep_group` (which fills the NULL DirectorSK/RegionSK/SectionSK of the `_last` dims), `dim_company` and the `dim_*_last` tables it reads.
- Approximate size (BigQuery metadata, 2026-10-31): 164 rows, 25.6 KB.

# Examples

Active units of one company with their parent.

```sql
SELECT unit_id, unit_level, unit_name, parent_unit_id, plan_code
FROM `databuffet-nonprd.org_center.org_center_unit`
WHERE company_id = 'ag01'
  AND CURRENT_DATE('Asia/Bangkok') BETWEEN valid_from AND valid_to
ORDER BY depth, unit_id
```

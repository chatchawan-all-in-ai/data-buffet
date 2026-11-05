---
type: BigQuery Table
title: "org_center_person"
description: "One row = one person (across all companies) in the org center, with name, contact, LINE UUID, companies, current positions and an active flag."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_person&page=table"
project_id: databuffet-nonprd
dataset_id: org_center
table_id: org_center_person
tags: ["org_center", "mds", "dimension_daily", "org_center"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_person.sqlx"
    title: "Dataform definition (org_center/org_center_person.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

The who-is-who list of the org center (the TA app's 'employees'), built from [org_center_member](/org_center/org_center_member.md) plus contact data from MDS (mds_data_employee_info: email, mobile phone, LINE UUID). Where org_center_member says where a person sits and when, this table gives one deterministic row per person.

Read by: [org_center_flags](/org_center/org_center_flags.md), [export_employees](/view/pub_sub/export_employees.md).

# Grain and key

One row per `employee_id` (never NULL), even when the person works in two companies. Contact-only employees (in MDS but without a member row) do not create person rows. Placeholder managers (Non Director, 9999990 to 9999999) get a row like anyone else.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_id` | STRING | MDS employee code, taken from org_center_member.employee_id. |
| `first_name` | STRING | First name picked from the person's member rows: the first row that is not CEO or DIRECTOR in the pick order (a person with only DIRECTOR/CEO rows gets the DIRECTOR name, then the CEO name, split at the first space). Personal data. |
| `last_name` | STRING | Surname picked by the same rule. Personal data. |
| `nickname` | STRING | First non-NULL nickname in the pick order (CEO and DIRECTOR rows have none). |
| `email` | STRING | First non-NULL member email in the pick order; only when no non-NULL member email exists falls back to mds_data_employee_info.Email. An empty string is non-NULL and blocks that fallback. |
| `mobile_phone` | STRING | mds_data_employee_info.MobilePhone by EmployeeID (active rows, latest updated_at then lowest id), as entered with no cleaning; NULL when absent. |
| `line_uuid` | STRING | mds_data_employee_info.LineUUID by EmployeeID (same active row as mobile_phone), as entered with no cleaning; NULL when absent. |
| `company_id` | `ARRAY<STRING>` | Sorted ARRAY of every company_id found in the person's member rows. |
| `position_code` | `ARRAY<STRING>` | ARRAY of distinct positions with a member row valid today, ordered CEO, DIRECTOR, REGION_MGR, SECTION_MGR, TA, PC_MDT, PC_AGENT; empty when none is valid. |
| `is_active` | BOOL | TRUE when the person has at least one member row valid today (CURRENT_DATE in Asia/Bangkok between valid_from and valid_to). |

# How it is built

- Definition: `definitions/org_center/org_center_person.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `employee_id`.
- Storage options: `{"clusterBy": ["employee_id"]}`.
- Reads: [org_center.org_center_member](/org_center/org_center_member.md), `mds_dataset.mds_data_employee_info` (master data loaded outside this repo).
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Runs after `org_center_schema` and `org_center_member`; also reads mds_data_employee_info (master data loaded outside this repo).

# Examples

Active people holding the TA position.

```sql
SELECT employee_id, company_id, position_code
FROM `databuffet-nonprd.org_center.org_center_person`
WHERE is_active AND 'TA' IN UNNEST(position_code)
```

People who work in more than one company.

```sql
SELECT employee_id, company_id
FROM `databuffet-nonprd.org_center.org_center_person`
WHERE ARRAY_LENGTH(company_id) > 1
```

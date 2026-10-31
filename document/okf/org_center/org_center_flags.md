---
type: BigQuery Table
title: "org_center_flags"
description: "One row = one data-quality problem found in the org-center tables (unit, member, person or link)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_flags&page=table"
tags: ["org_center", "mds", "dimension_daily", "org_center"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_flags.sqlx"
    title: "Dataform definition (org_center/org_center_flags.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Report-only data-quality table of the org center, rebuilt nightly: it lists problems found in [org_center_unit](/org_center/org_center_unit.md), [org_center_member](/org_center/org_center_member.md), [org_center_person](/org_center/org_center_person.md) and [org_center_link](/org_center/org_center_link.md) (input = output; nothing is fixed or hidden in those tables). The rules follow the Check sheet of Org_Mock_Master_Plan_v4.xlsx.

# Grain and key

One row per problem: `entity` + `entity_key` + `rule_code`. `entity_key` is a JSON array of the key components of the flagged row (company: company_id; unit: company, unit_id; member: its 5 key columns; person: employee_id; link: its 5 key columns; dates as ISO strings; NULL kept as JSON null). No declared key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company of the flagged row; NULL for person-level rules. |
| `entity` | STRING | What was flagged: UNIT, MEMBER, PERSON, LINK or COMPANY. |
| `entity_key` | STRING | JSON array text of the flagged row's key components (grain above). |
| `rule_code` | STRING | Rule that fired: DUPLICATE_ID, MEMBER_NO_PERSON, MEMBER_NO_UNIT, UNIT_NO_PARENT (DIVISION/REGION/SECTION whose parent unit is missing), UNIT_NO_MANAGER (DIVISION/REGION/SECTION valid today without a manager of its level valid today; COMPANY units are excluded), COMPANY_NO_CEO (an active company in `mds_data_company_master` with an empty `CEOEmpID`), PC_TA_UNKNOWN_PC, PC_TA_UNKNOWN_TA, PC_TA_UNKNOWN_BRANCH, PC_TA_OVERLAP, PHONE_FORMAT, PHONE_DUPLICATE. |
| `rule_description` | STRING | Thai description of the rule. |

# How it is built

- Definition: `definitions/org_center/org_center_flags.sqlx` (`type: "table"`, tags `dimension_daily`).
- Storage options: `{"clusterBy": ["rule_code", "entity"]}`.
- Reads: [org_center.org_center_unit](/org_center/org_center_unit.md), [org_center.org_center_member](/org_center/org_center_member.md), [org_center.org_center_person](/org_center/org_center_person.md), [org_center.org_center_link](/org_center/org_center_link.md), `mds_dataset.mds_data_mdt_sales_pc_master` (master data loaded outside this repo), `mds_dataset.mds_data_mdt_sales_branch_master` (master data loaded outside this repo), `mds_dataset.mds_data_company_master` (master data loaded outside this repo).
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Depends on the four other org_center tables; also reads mds_data_mdt_sales_pc_master and mds_data_mdt_sales_branch_master (master data loaded outside this repo).
- Approximate size (BigQuery metadata, 2026-10-31): 2 rows, 406 B.

# Examples

Problems by rule.

```sql
SELECT rule_code, entity, COUNT(*) AS n
FROM `databuffet-nonprd.org_center.org_center_flags`
GROUP BY rule_code, entity
ORDER BY n DESC
```

Units that currently have no manager.

```sql
SELECT company_id, entity_key, rule_description
FROM `databuffet-nonprd.org_center.org_center_flags`
WHERE rule_code = 'UNIT_NO_MANAGER'
```

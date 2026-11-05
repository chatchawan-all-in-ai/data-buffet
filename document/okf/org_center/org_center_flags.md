---
type: BigQuery Table
title: "org_center_flags"
description: "One row = one data-quality problem found in the org-center tables (unit, member, person, link, customer portfolio or exception)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=org_center&t=org_center_flags&page=table"
project_id: databuffet-nonprd
dataset_id: org_center
table_id: org_center_flags
tags: ["org_center", "mds", "dimension_daily", "org_center"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/org_center/org_center_flags.sqlx"
    title: "Dataform definition (org_center/org_center_flags.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/org_center/org-center.md"
    title: "Data Mart wiki (document/project_wiki/org_center/org-center.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Report-only data-quality table of the org center, rebuilt nightly: it lists problems found in [org_center_unit](/org_center/org_center_unit.md), [org_center_member](/org_center/org_center_member.md), [org_center_person](/org_center/org_center_person.md), [org_center_link](/org_center/org_center_link.md), [org_center_customer_ta](/org_center/org_center_customer_ta.md) and [org_center_exception](/org_center/org_center_exception.md) (input = output; nothing is fixed or hidden in those tables). The rules follow the Check sheet of Org_Mock_Master_Plan_v4.xlsx.

# Grain and key

One row = one data-quality problem found in an org-center table: `entity` + `entity_key` + `rule_code`. No declared key. The [Org Center flags reference](../../project_wiki/org_center/org-center.md#org_center_flags) owns the entity values, key encoding and rule conditions, including the per-scope EXCEPTION_NO_EMPLOYEE rule.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company of the flagged row; NULL for person-level rules. |
| `entity` | STRING | Flagged entity type; see the flags reference above. |
| `entity_key` | STRING | JSON array text of the flagged row's key components; encoding is defined in the flags reference above. |
| `rule_code` | STRING | Rule identifier; the flags reference above defines each condition, including EXCEPTION_NO_EMPLOYEE. |
| `rule_description` | STRING | Thai description of the rule. |

# How it is built

- Definition: `definitions/org_center/org_center_flags.sqlx` (`type: "table"`, tags `dimension_daily`).
- Storage options: `{"clusterBy": ["rule_code", "entity"]}`.
- Reads: [org_center.org_center_unit](/org_center/org_center_unit.md), [org_center.org_center_member](/org_center/org_center_member.md), [org_center.org_center_person](/org_center/org_center_person.md), [org_center.org_center_link](/org_center/org_center_link.md), [org_center.org_center_customer_ta](/org_center/org_center_customer_ta.md), [org_center.org_center_exception](/org_center/org_center_exception.md), `mds_dataset.mds_data_mdt_sales_pc_master` (master data loaded outside this repo), `mds_dataset.mds_data_mdt_sales_branch_master` (master data loaded outside this repo), `mds_dataset.mds_data_company_master` (master data loaded outside this repo).
- Full nightly rebuild (`type: "table"`, tag `dimension_daily`; `org_center_schema` creates the dataset). Runs after the six other org_center tables (`org_center_schema` is also declared); also reads mds_data_mdt_sales_pc_master, mds_data_mdt_sales_branch_master and mds_data_company_master (master data loaded outside this repo).

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

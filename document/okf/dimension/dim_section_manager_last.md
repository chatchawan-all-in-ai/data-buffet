---
type: BigQuery Table
title: "dim_section_manager_last"
description: "One row = one section code (companyID, SectionID) with its latest section manager interval from dim_section_manager."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_section_manager_last&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_section_manager_last
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_section_manager_last.sqlx"
    title: "Dataform definition (dimension/dim_section_manager_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Latest-row snapshot of [dim_section_manager](/dimension/dim_section_manager.md): one manager per section with no validity filtering, used by the `*Last` reports (`dim_target_product_group_by_sale`, org-center members, RLS views, customer-report info, Model_* views).

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [org_center_member](/org_center/org_center_member.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [view_rls_data](/view/process_dataset/view_rls_data.md).

# Grain and key

One row per `(CompanyID, SectionID)`: the row with the greatest EndDate (ties by StartDate) is kept. `SectionManagerSK` is renumbered here (ordered by CompanySK, SectionID), not equal to `dim_section_manager.SectionManagerSK`. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `SectionManagerSK` | INT64 | Surrogate key of this snapshot, `ROW_NUMBER()` ordered by CompanySK, SectionID. Target of the hierarchy keys in `dim_section_last` and `dim_department_last`. Regenerated every run. |
| `CompanySK` | INT64 | Company surrogate key re-joined from dim_company. |
| `companyID` | STRING | Company code from dim_company.companyID. |
| `SectionID` | STRING | Section code from dim_section_manager.SectionID. |
| `SectionName` | STRING | Section name on the kept interval. |
| `SectionManagerEmployeeID` | STRING | Employee code of the manager on the kept interval. |
| `SectionManagerName` | STRING | Manager given name (kept interval). |
| `SectionManagerSurname` | STRING | Manager surname (kept interval). |
| `SectionManagerNickname` | STRING | Manager nickname (kept interval). |
| `StartDate` | DATE | Start of the kept interval. |
| `EndDate` | DATE | End of the kept interval. |

# How it is built

- Definition: `definitions/dimension/dim_section_manager_last.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `SectionManagerSK`.
- Storage options: `{"clusterBy": ["SectionManagerSK"]}`.
- Reads: [dimension_table.dim_section_manager](/dimension/dim_section_manager.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`) from dim_section_manager + dim_company, tag `dimension_daily`; runs before `update_sk_sale_rep_group` and `dim_target_product_group_by_sale`.
- Approximate size (BigQuery metadata, 2026-10-31): 127 rows, 18.0 KB.

# Examples

Section manager per section code from the snapshot.

```sql
SELECT companyID, SectionID, SectionManagerEmployeeID, EndDate
FROM `databuffet-nonprd.dimension_table.dim_section_manager_last`
ORDER BY companyID, SectionID;
```

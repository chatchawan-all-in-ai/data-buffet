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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Latest-row snapshot of [dim_section_manager](/dimension/dim_section_manager.md): one manager per section with no validity filtering, for the `*Last` joins.

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [org_center_member](/org_center/org_center_member.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_rls_data](/view/process_dataset/view_rls_data.md), update_sk_sale_rep_group.

# Grain and key

One row = one section code. Natural key: (`companyID`, `SectionID`, `StartDate`, `EndDate`). `SectionManagerSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `SectionManagerSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
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

- Definition: `definitions/dimension/dim_section_manager_last.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: [dimension_table.dim_section_manager](/dimension/dim_section_manager.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company and dim_section_manager.
# Examples

Section manager per section code from the snapshot.

```sql
SELECT companyID, SectionID, SectionManagerEmployeeID, EndDate
FROM `databuffet-nonprd.dimension_table.dim_section_manager_last`
ORDER BY companyID, SectionID;
```

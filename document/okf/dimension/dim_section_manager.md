---
type: BigQuery Table
title: "dim_section_manager"
description: "One row = one section manager assignment for one section of one company over one StartDate to EndDate interval, from the MDS section manager master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_section_manager&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_section_manager
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_section_manager.sqlx"
    title: "Dataform definition (dimension/dim_section_manager.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Says who manages each section and when (employee ID plus name parts). It supplies `SectionManagerSK` to `fact_transcation` and `view_fact_transcation`, and the target-by-agent day-of-work view; [dim_section_manager_last](/dimension/dim_section_manager_last.md) is the latest-row snapshot.

Read by: [dim_section_manager_last](/dimension/dim_section_manager_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [fact_transcation](/fact/fact_transcation.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one active MDS section manager assignment. Natural key: (`companyID`, `SectionID`, `StartDate`, `EndDate`). `SectionManagerSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `SectionManagerSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `SectionID` | STRING | Section code managed; joins to dim_section.SectionID and dim_department.SectionID. |
| `SectionName` | STRING | Section name as entered in the manager master. |
| `SectionManagerEmployeeID` | STRING | Employee code of the section manager (person identifier). |
| `SectionManagerName` | STRING | Manager given name. |
| `SectionManagerSurname` | STRING | Manager surname. |
| `SectionManagerNickname` | STRING | Manager nickname. |
| `StartDate` | DATE | First date this assignment is valid (MDS DATE). |
| `EndDate` | DATE | Last date this assignment is valid (MDS DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_sales_section_manager_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_section_manager.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_sales_section_manager_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Current manager of each section.

```sql
SELECT companyID, SectionID, SectionName, SectionManagerEmployeeID
FROM `databuffet-nonprd.dimension_table.dim_section_manager`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

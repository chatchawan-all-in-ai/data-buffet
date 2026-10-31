---
type: BigQuery Table
title: "dim_section_manager"
description: "One row = one section manager assignment for one section of one company over one StartDate to EndDate interval, from the MDS section manager master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_section_manager&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_section_manager.sqlx"
    title: "Dataform definition (dimension/dim_section_manager.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Says who manages each section and when (employee ID plus name parts). It supplies `SectionManagerSK` to `fact_transcation` and `view_fact_transcation`, and the target-by-agent day-of-work view; [dim_section_manager_last](/dimension/dim_section_manager_last.md) is the latest-row snapshot.

Read by: [dim_section_manager_last](/dimension/dim_section_manager_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per active MDS row, ordered and SK-numbered by companyID, SectionID, StartDate, EndDate. A section that changed manager has one row per interval. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `SectionManagerSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by companyID, SectionID, StartDate, EndDate. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `SectionID` | STRING | Section code managed; joins to dim_section.SectionID and dim_department.SectionID. |
| `SectionName` | STRING | Section name as entered in the manager master. |
| `SectionManagerEmployeeID` | STRING | Employee code of the section manager (person identifier). |
| `SectionManagerName` | STRING | Manager given name. |
| `SectionManagerSurname` | STRING | Manager surname. |
| `SectionManagerNickname` | STRING | Manager nickname. |
| `StartDate` | DATE | First date this assignment is valid (MDS DATE). |
| `EndDate` | DATE | Last date this assignment is valid (MDS DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_data_sales_section_manager_master`; trace column. |

# How it is built

- Definition: `definitions/dimension/dim_section_manager.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `SectionManagerSK`.
- Storage options: `{"clusterBy": ["SectionManagerSK"]}`.
- Reads: `mds_dataset.mds_data_sales_section_manager_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; `CREATE OR REPLACE` each run from `mds_dataset` (loaded outside this repo). Runs after `dim_company`. Reads `mds_data_sales_section_manager_master`.
- Approximate size (BigQuery metadata, 2026-10-31): 177 rows, 31.4 KB.

# Examples

Current manager of each section.

```sql
SELECT companyID, SectionID, SectionName, SectionManagerEmployeeID
FROM `databuffet-nonprd.dimension_table.dim_section_manager`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

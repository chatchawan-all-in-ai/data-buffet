---
type: BigQuery Table
title: "dim_section"
description: "One row = one sales section (SectionID) of one company over one StartDate to EndDate validity interval, from the MDS section master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_section&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_section.sqlx"
    title: "Dataform definition (dimension/dim_section.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Section master of the sales organisation (a section groups departments inside a region). Facts and views use `SectionSK` to show the section of a sale or target; `dim_section_last` is the one-row-per-section snapshot and `rls_customer360` uses it for row-level access.

Read by: [dim_section_last](/dimension/dim_section_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [rls_customer360](/process/rls_customer360.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per active MDS row, ordered and SK-numbered by companyID, SectionID, StartDate, EndDate. A section appears once per validity interval, so `(companyID, SectionID)` is not unique here. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `SectionSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by companyID, SectionID, StartDate, EndDate. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `SectionID` | STRING | Section code; joins to `dim_department.SectionID` and to `dim_section_manager.SectionID`. |
| `SectionName` | STRING | Display name of the section (MDS). |
| `StartDate` | DATE | First date the row is valid (MDS DATE). |
| `EndDate` | DATE | Last date the row is valid (MDS DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_data_sales_section_master`; trace column. |

# How it is built

- Definition: `definitions/dimension/dim_section.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `SectionSK`.
- Storage options: `{"clusterBy": ["SectionSK"]}`.
- Reads: `mds_dataset.mds_data_sales_section_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; `CREATE OR REPLACE` each run from `mds_dataset` (loaded outside this repo). Runs after `dim_company`. Reads `mds_data_sales_section_master`.
- Approximate size (BigQuery metadata, 2026-10-31): 170 rows, 18.3 KB.

# Examples

Sections valid today.

```sql
SELECT SectionSK, companyID, SectionID, SectionName
FROM `databuffet-nonprd.dimension_table.dim_section`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
ORDER BY companyID, SectionID;
```

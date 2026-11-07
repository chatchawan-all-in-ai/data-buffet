---
type: BigQuery Table
title: "dim_section_last"
description: "One row = one section code (companyID, SectionID) with its latest validity interval from dim_section, plus hierarchy keys up to manager, region and director."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_section_last&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_section_last
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_section_last.sqlx"
    title: "Dataform definition (dimension/dim_section_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Latest-row snapshot of [dim_section](/dimension/dim_section.md) with one row per section, for the `*Last` joins and the org-center tables. It also carries the hierarchy SKs (section manager, region, region manager, director) so a section can be walked upward.

Read by: [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md), [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [export_dim_section_last](/view/pub_sub/export_dim_section_last.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [org_center_member](/org_center/org_center_member.md), [org_center_unit](/org_center/org_center_unit.md), [rls_ta_customer](/process/rls_ta_customer.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [view_rls_data](/view/process_dataset/view_rls_data.md), [view_sales_representative_last](/view/dimension_view/view_sales_representative_last.md).

# Grain and key

One row = one section code. Natural key: (`companyID`, `SectionID`, `StartDate`, `EndDate`). `SectionSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `SectionSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `SectionManagerSK` | INT64 | Hierarchy key to [dim_section_manager_last](/dimension/dim_section_manager_last.md).SectionManagerSK. Built NULL, backfilled by `update_sk_sale_rep_group` (via `dim_department_last`). |
| `RegionSK` | INT64 | Hierarchy key to [dim_region_last](/dimension/dim_region_last.md).RegionSK. Built NULL, backfilled by `update_sk_sale_rep_group` from `dim_department_last`. |
| `RegionManagerSK` | INT64 | Hierarchy key to dim_region_manager_last. Built NULL, backfilled by `update_sk_sale_rep_group`. |
| `DirectorSK` | INT64 | Hierarchy key to dim_director_last. Built NULL, backfilled by `update_sk_sale_rep_group`. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code from dim_company.companyID. |
| `SectionID` | STRING | Section code, from dim_section.SectionID. |
| `SectionName` | STRING | Section name from the kept interval. |
| `StartDate` | DATE | Start of the kept validity interval. |
| `EndDate` | DATE | End of the kept validity interval. |
# How it is built

- Definition: `definitions/dimension/dim_section_last.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company and dim_section. The four hierarchy SKs are then filled by the operation `update_sk_sale_rep_group`.
# Examples

Sections with their section manager (via the hierarchy key).

```sql
SELECT s.companyID, s.SectionID, s.SectionName, m.SectionManagerEmployeeID
FROM `databuffet-nonprd.dimension_table.dim_section_last` AS s
LEFT JOIN `databuffet-nonprd.dimension_table.dim_section_manager_last` AS m
  ON s.SectionManagerSK = m.SectionManagerSK
ORDER BY s.companyID, s.SectionID;
```

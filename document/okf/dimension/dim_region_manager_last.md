---
type: BigQuery Table
title: "dim_region_manager_last"
description: "One row = one region or sub-region code (companyID, RegionID, SubRegionID) with its latest region manager interval from dim_region_manager."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_region_manager_last&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_region_manager_last
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_region_manager_last.sqlx"
    title: "Dataform definition (dimension/dim_region_manager_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Latest-row snapshot of [dim_region_manager](/dimension/dim_region_manager.md): one manager per region code, with no validity filtering. It is the manager lookup of the `*Last` joins.

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [org_center_member](/org_center/org_center_member.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_rls_data](/view/process_dataset/view_rls_data.md), update_sk_sale_rep_group.

# Grain and key

One row = one region or sub-region code. Natural key: (`companyID`, `RegionID`, `SubRegionID`, `StartDate`, `EndDate`). `RegionManagerSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `RegionManagerSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code from dim_company.companyID. |
| `RegionID` | STRING | Region code, from dim_region_manager.RegionID. |
| `SubRegionID` | STRING | Sub-region code, from dim_region_manager.SubRegionID. |
| `RegionName` | STRING | Region name from the kept interval. |
| `RegionManagerEmployeeID` | STRING | Employee code of the manager on the kept interval. |
| `RegionManagerName` | STRING | Manager given name (kept interval). |
| `RegionManagerSurname` | STRING | Manager surname (kept interval). |
| `RegionManagerNickname` | STRING | Manager nickname (kept interval). |
| `StartDate` | DATE | Start of the kept interval. |
| `EndDate` | DATE | End of the kept interval. |
# How it is built

- Definition: `definitions/dimension/dim_region_manager_last.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company and dim_region_manager.
# Examples

Manager per region code from the snapshot.

```sql
SELECT companyID, RegionID, SubRegionID, RegionManagerEmployeeID, EndDate
FROM `databuffet-nonprd.dimension_table.dim_region_manager_last`
ORDER BY companyID, RegionID, SubRegionID;
```

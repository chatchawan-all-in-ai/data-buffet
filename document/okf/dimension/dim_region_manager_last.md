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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Latest-row snapshot of [dim_region_manager](/dimension/dim_region_manager.md): one manager per region code, with no validity filtering. It is the manager lookup used by the `*Last` reports (`view_fact_transcation`, `dim_target_product_group_by_sale`, org-center members, RLS views, customer-report info).

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [org_center_member](/org_center/org_center_member.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [view_rls_data](/view/process_dataset/view_rls_data.md).

# Grain and key

One row per `(CompanyID, RegionID, SubRegionID)`: row with the greatest EndDate (ties by StartDate) is kept. `RegionManagerSK` is renumbered here (ordered by CompanySK, RegionID, SubRegionID) and differs from `dim_region_manager.RegionManagerSK`. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `RegionManagerSK` | INT64 | Surrogate key of this snapshot, `ROW_NUMBER()` ordered by CompanySK, RegionID, SubRegionID. Target of `dim_region_last.RegionManagerSK` after `update_sk_sale_rep_group`. Regenerated every run. |
| `CompanySK` | INT64 | Company surrogate key re-joined from dim_company by companyID. |
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

- Definition: `definitions/dimension/dim_region_manager_last.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `RegionManagerSK`.
- Storage options: `{"clusterBy": ["RegionManagerSK"]}`.
- Reads: [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`) from dim_region_manager + dim_company, tag `dimension_daily`; finishes before `update_sk_sale_rep_group` and `dim_target_product_group_by_sale`.
- Approximate size (BigQuery metadata, 2026-10-31): 28 rows, 3.5 KB.

# Examples

Manager per region code from the snapshot.

```sql
SELECT companyID, RegionID, SubRegionID, RegionManagerEmployeeID, EndDate
FROM `databuffet-nonprd.dimension_table.dim_region_manager_last`
ORDER BY companyID, RegionID, SubRegionID;
```

---
type: BigQuery Table
title: "dim_region_last"
description: "One row = one region or sub-region code (companyID, RegionID, SubRegionID) of a company, keeping only its latest validity interval from dim_region."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_region_last&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_region_last
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_region_last.sqlx"
    title: "Dataform definition (dimension/dim_region_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Latest-row snapshot of [dim_region](/dimension/dim_region.md) with one row per region code, used for joins with one row per region code (the `*Last` columns of `view_fact_transcation`, `dim_target_product_group_by_sale`, org-center units, RLS). It also carries the hierarchy keys `RegionManagerSK` and `DirectorSK` so a region can be walked up to its manager and director.

Read by: [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md), [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [org_center_unit](/org_center/org_center_unit.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_sales_representative_last](/view/dimension_view/view_sales_representative_last.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [view_rls_data](/view/process_dataset/view_rls_data.md).

# Grain and key

One row per `(CompanyID, RegionID, SubRegionID)`: the row with the greatest EndDate (ties by StartDate) is kept; the old `CURRENT_DATE between StartDate and EndDate` filter is commented out, so expired regions stay. `RegionSK` is renumbered by this table (ordered by CompanySK, RegionID, SubRegionID) and is **not** the SK of dim_region. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `RegionSK` | INT64 | Surrogate key of this snapshot, `ROW_NUMBER()` ordered by CompanySK, RegionID, SubRegionID. Different from `dim_region.RegionSK`. Regenerated every run. |
| `RegionManagerSK` | INT64 | Hierarchy key to [dim_region_manager_last](/dimension/dim_region_manager_last.md).RegionManagerSK. Built as NULL, then backfilled by `update_sk_sale_rep_group` (join on RegionID, SubRegionID, CompanySK). NULL until that step has run. |
| `DirectorSK` | INT64 | Hierarchy key to [dim_director_last](/dimension/dim_director_last.md).DirectorSK. Built as NULL, then backfilled by `update_sk_sale_rep_group` (join on DirectorID + CompanySK). |
| `CompanySK` | INT64 | Company surrogate key, taken from dim_company by companyID (re-joined, not copied from dim_region). |
| `companyID` | STRING | Company code from dim_company.companyID. |
| `DirectorID` | STRING | Director code carried over from dim_region.DirectorID; used by update_sk_sale_rep_group to find DirectorSK. |
| `RegionID` | STRING | Region code, from dim_region.RegionID. |
| `SubRegionID` | STRING | Sub-region code, from dim_region.SubRegionID. |
| `RegionName` | STRING | Region name of the kept (latest) interval, from dim_region.RegionName. |
| `StartDate` | DATE | Start of the kept validity interval (dim_region.StartDate). |
| `EndDate` | DATE | End of the kept validity interval (dim_region.EndDate). |

# How it is built

- Definition: `definitions/dimension/dim_region_last.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `RegionSK`.
- Storage options: `{"clusterBy": ["RegionSK"]}`.
- Reads: [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`) from dim_region + dim_company, tag `dimension_daily`. `RegionManagerSK` and `DirectorSK` are then UPDATEd in place by the operation `update_sk_sale_rep_group` (depends on all `_last` dims), the keys are available after that operation.
- Approximate size (BigQuery metadata, 2026-10-31): 28 rows, 2.6 KB.

# Examples

One row per region code with its manager and director keys resolved.

```sql
SELECT r.companyID, r.RegionID, r.SubRegionID, r.RegionName, m.RegionManagerEmployeeID
FROM `databuffet-nonprd.dimension_table.dim_region_last` AS r
LEFT JOIN `databuffet-nonprd.dimension_table.dim_region_manager_last` AS m
  ON r.RegionManagerSK = m.RegionManagerSK
ORDER BY r.companyID, r.RegionID, r.SubRegionID;
```

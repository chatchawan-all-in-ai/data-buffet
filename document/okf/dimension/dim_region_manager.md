---
type: BigQuery Table
title: "dim_region_manager"
description: "One row = one region manager assignment for a region or sub-region of one company over one StartDate to EndDate interval, from the MDS region manager master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_region_manager&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_region_manager
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_region_manager.sqlx"
    title: "Dataform definition (dimension/dim_region_manager.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Says who manages each region (and sub-region) and when, with the manager's employee ID and name parts. Facts and views take it through `RegionManagerSK` to show the Region Manager on sales and target reports (MDT saleout/target facts, `view_fact_transcation`, target-by-agent views). [dim_region_manager_last](/dimension/dim_region_manager_last.md) is its latest-row snapshot.

Read by: [dim_region_manager_last](/dimension/dim_region_manager_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md), [fact_target_series_mdt](/fact/fact_target_series_mdt.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per active MDS row, ordered and SK-numbered by companyID, RegionID, SubRegionID, StartDate, EndDate. A region that changed manager has one row per interval; the natural key is `(companyID, RegionID, SubRegionID, StartDate, EndDate)`. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `RegionManagerSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by companyID, RegionID, SubRegionID, StartDate, EndDate. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `RegionID` | STRING | Region code managed; joins to dim_region.RegionID. |
| `SubRegionID` | STRING | Sub-region code managed; joins to dim_region.SubRegionID. |
| `RegionName` | STRING | Region name as entered in the manager master. |
| `RegionManagerEmployeeID` | STRING | Employee code of the region manager (a person identifier; describes the column only). |
| `RegionManagerName` | STRING | Manager given name. |
| `RegionManagerSurname` | STRING | Manager surname. |
| `RegionManagerNickname` | STRING | Manager nickname. |
| `StartDate` | DATE | First date this manager assignment is valid (MDS DATE). |
| `EndDate` | DATE | Last date this manager assignment is valid (MDS DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_data_sales_region_manager_master`; trace column. |

# How it is built

- Definition: `definitions/dimension/dim_region_manager.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `RegionManagerSK`.
- Storage options: `{"clusterBy": ["RegionManagerSK"]}`.
- Reads: `mds_dataset.mds_data_sales_region_manager_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; `CREATE OR REPLACE` each run from `mds_dataset` (loaded outside this repo). Runs after `dim_company`. Reads `mds_data_sales_region_manager_master`.
- Approximate size (BigQuery metadata, 2026-10-31): 57 rows, 9.3 KB.

# Examples

Current manager of every region.

```sql
SELECT companyID, RegionID, SubRegionID, RegionManagerEmployeeID
FROM `databuffet-nonprd.dimension_table.dim_region_manager`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

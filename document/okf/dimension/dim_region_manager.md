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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Says who manages each region (and sub-region) and when, with the manager's employee ID and name parts. Facts and views take it through `RegionManagerSK` to show the Region Manager on sales and target reports (MDT saleout/target facts, `view_fact_transcation`, target-by-agent views). [dim_region_manager_last](/dimension/dim_region_manager_last.md) is its latest-row snapshot.

Read by: [dim_region_manager_last](/dimension/dim_region_manager_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md), [fact_target_series_mdt](/fact/fact_target_series_mdt.md), [fact_transcation](/fact/fact_transcation.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one active MDS region manager assignment. Natural key: (`companyID`, `RegionID`, `SubRegionID`, `StartDate`, `EndDate`). `RegionManagerSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `RegionManagerSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
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
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_sales_region_manager_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_region_manager.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_sales_region_manager_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Current manager of every region.

```sql
SELECT companyID, RegionID, SubRegionID, RegionManagerEmployeeID
FROM `databuffet-nonprd.dimension_table.dim_region_manager`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

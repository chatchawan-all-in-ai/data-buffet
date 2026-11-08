---
type: BigQuery Table
title: "dim_director"
description: "One row = one sales director (company, DirectorID) with the director of sales and a validity period, from the MDS sales-director master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_director&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_director
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_director.sqlx"
    title: "Dataform definition (dimension/dim_director.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Director level of the sales organisation. Each row names a director and the director of sales for a date range. Source: mds `mds_data_sales_director_master`.

Read by: [dim_director_last](/dimension/dim_director_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md), [fact_target_series_mdt](/fact/fact_target_series_mdt.md), [fact_transcation](/fact/fact_transcation.md), [rls_customer360](/process/rls_customer360.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_salein_director_mdt](/view/fact_view/view_fact_salein_director_mdt.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one director period. Natural key: (`companyID`, `DirectorID`, `StartDate`, `EndDate`). `DirectorSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `DirectorSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `DirectorID` | STRING | Pass-through of mds `DirectorID`, cleaned with `cleanString` (empty string becomes NULL). Director code; with company it identifies the director over time. |
| `DirectorName` | STRING | Pass-through of mds `DirectorName`, cleaned with `cleanString` (empty string becomes NULL). Director name. |
| `DirectorOfSalesID` | STRING | Pass-through of mds `DirectorOfSalesID`, cleaned with `cleanString` (empty string becomes NULL). Code of the director of sales above this director. |
| `DirectorOfSalesName` | STRING | Pass-through of mds `DirectorOfSalesName`, cleaned with `cleanString` (empty string becomes NULL). Name of the director of sales. |
| `StartDate` | DATE | First day the director assignment is valid (mds `StartDate`, DATE). |
| `EndDate` | DATE | Last day the assignment is valid (mds `EndDate`, DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_sales_director_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_director.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_sales_director_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Directors valid today with their director of sales.

```sql
SELECT companyID, DirectorID, DirectorName, DirectorOfSalesID
FROM `databuffet-nonprd.dimension_table.dim_director`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

Director row counts per company.

```sql
SELECT companyID, COUNT(*) AS rows_n, COUNT(DISTINCT DirectorID) AS directors
FROM `databuffet-nonprd.dimension_table.dim_director`
GROUP BY 1;
```

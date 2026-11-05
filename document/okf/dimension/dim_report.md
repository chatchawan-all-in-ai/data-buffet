---
type: BigQuery Table
title: "dim_report"
description: "One row = one report-group mapping of a company: a ReportID tied to a RegionID and optionally a MarketingGroupID, with two display names, from the MDS report group master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_report&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_report
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_report.sqlx"
    title: "Dataform definition (dimension/dim_report.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Maps a region (and, when a region is split by product group, a marketing group) to the report group used for the Region Transaction reports. `fact_saleout_mdt`, `fact_saleout_monthly_mdt`, `view_fact_transcation`, `dim_target_product_group_by_sale` and the Model_* views take `ReportSK` from it. The matching logic lives in the consumers (see Segment under Grain and key).

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one active MDS report-group row: key `ReportSK`, `ROW_NUMBER()` ordered by companyID, ReportID, RegionID, MarketingGroupID. A `Segment` value (1, 2 or 3) is **not stored**; `view_fact_transcation` and `dim_target_product_group_by_sale` derive it per RegionID: only one row for the RegionID gives 1 (match on RegionID); more than one row and MarketingGroupID NULL gives 3 (RegionID-only catch-all row); otherwise 2 (RegionID plus MarketingGroupID). No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `ReportSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by companyID, ReportID, RegionID, MarketingGroupID. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `ReportID` | STRING | Report group code from MDS. |
| `RegionID` | STRING | Region code the report group covers; matched to dim_region.RegionID (or `dim_region_last.RegionID`) by consumers. |
| `MarketingGroupID` | STRING | Marketing (product) group code that narrows the report group; NULL means the row applies to the region regardless of group. Matched to the marketing group of the product (for example `stk_mkt.MarketingGroupID`). |
| `ReportName1` | STRING | First display name of the report group (MDS). |
| `ReportName2` | STRING | Second display name of the report group (MDS). |
| `MdsID` | STRING | `id` of the source row in `mds_data_sales_report_group_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_report.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `ReportSK`.
- Storage options: `{"clusterBy": ["ReportSK"]}`.
- Reads: `mds_dataset.mds_data_sales_report_group_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Report-group rows with the Segment value the consumers derive.

```sql
SELECT ReportSK, companyID, ReportID, RegionID, MarketingGroupID,
  CASE WHEN COUNT(*) OVER (PARTITION BY RegionID) = 1 THEN 1
       WHEN MarketingGroupID IS NULL THEN 3 ELSE 2 END AS Segment
FROM `databuffet-nonprd.dimension_table.dim_report`
ORDER BY RegionID, Segment;
```

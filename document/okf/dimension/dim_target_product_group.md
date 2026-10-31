---
type: BigQuery Table
title: "dim_target_product_group"
description: "One row = one company-level sales target (Amt and Qty) for a year and month by marketing group, sub group, segment, channel target group and TargetID, from the MDS target by product group master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_target_product_group&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_target_product_group.sqlx"
    title: "Dataform definition (dimension/dim_target_product_group.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Target amounts before they are split among employees. `dim_target_product_group_by_sale` joins it to [dim_rate_target](/dimension/dim_rate_target.md) to allocate the target by employee, and `view_dim_target_by_agent` and `Model_Target_DayOfWork` consume the result.

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md).

# Grain and key

One row per active MDS row, SK ordered by companyID, Year, Month, MarketingGroupID, SubMarketingID, SegmentID, ChannelTargetGroup, TargetID. Natural key is that same tuple (uniqueness not enforced). No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetProductGroupSK` | INT64 | Surrogate key, `ROW_NUMBER()` over the key tuple above. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `Year` | INT64 | Target year (INT64 via `castInt64`). |
| `Month` | INT64 | Target month (INT64 via `castInt64`). |
| `MarketingGroupID` | STRING | Marketing group code of the target; matches `dim_product_mkt.MarketingGroupID` and `dim_rate_target.ProductGroupID`. |
| `MarketingGroupName` | STRING | Name of the marketing group. |
| `SubMarketingID` | STRING | Sub marketing group code. |
| `SubMarketingName` | STRING | Name of the sub marketing group. |
| `SegmentID` | STRING | Segment code. |
| `SegmentName` | STRING | Segment name. |
| `ChannelTargetGroup` | STRING | Sales channel group the target belongs to (meaning of values not documented in the repo). |
| `TargetID` | STRING | Target code; the join key to `dim_rate_target.TargetID` (with CompanySK, Year, Month). |
| `Amt` | FLOAT64 | Target amount (FLOAT64 via `castFloat64`, currency amount; assumed THB, not stated in the code). |
| `Qty` | FLOAT64 | Target quantity (FLOAT64 via `castFloat64`). |
| `MdsId` | STRING | `id` of the source row in `mds_data_sales_target_by_product_group_master` (selected as MdsID in SQL); trace column. Dropped by dim_target_product_group_by_sale. |

# How it is built

- Definition: `definitions/dimension/dim_target_product_group.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `TargetProductGroupSK`.
- Storage options: `{"clusterBy": ["TargetProductGroupSK"]}`.
- Reads: `mds_dataset.mds_data_sales_target_by_product_group_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; `CREATE OR REPLACE` each run from `mds_dataset` (loaded outside this repo). Runs after `dim_company`. Reads `mds_data_sales_target_by_product_group_master`.
- Approximate size (BigQuery metadata, 2026-10-31): 54,564 rows, 11.4 MB.

# Examples

Target by marketing group for the current year.

```sql
SELECT Month, MarketingGroupID, MarketingGroupName, TargetID, SUM(Amt) AS target_amt, SUM(Qty) AS target_qty
FROM `databuffet-nonprd.dimension_table.dim_target_product_group`
WHERE companyID = 'ag01' AND Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2;
```

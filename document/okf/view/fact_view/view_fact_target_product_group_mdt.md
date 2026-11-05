---
type: BigQuery View
title: "view_fact_target_product_group_mdt"
description: "One row = one day x marketing product group x report line x region/manager/director combination of the MDT-channel sales target, aggregated from dim_target_product_group_by_sale_dayofwork."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_target_product_group_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_target_product_group_mdt
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_target_product_group_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_target_product_group_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The sales target of the modern-trade channel, rolled up from the by-sale day-of-work target dimension. [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md) holds one row per sales person, department, product group and day; this view keeps only `ChannelTargetGroup = 'MDT'` and sums the new daily amount/quantity to the region/manager/director level, dropping the sale-rep, department and section levels.

No other repo object reads it.

# Grain and key

One row = one target group: key `Date`, `ProductMktSK`, `ReportSK`, `RegionSK`, `RegionManagerSK`, `DirectorSK`, `RegionSKLast`, `RegionManagerSKLast`, `DirectorSKLast` (unique). `GROUP BY 1..9` over `ChannelTargetGroup = 'MDT'` rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `Date` | DATE | Calendar date of the daily target (monthly target spread over the working days of the month). |
| `ProductMktSK` | INT64 | SK of `dim_product_mkt` (marketing group/sub-group/segment) the target belongs to. |
| `ReportSK` | INT64 | SK of `dim_report` line of the target. |
| `RegionSK` | INT64 | SK of `dim_region` for the target's sale-rep assignment on that date. |
| `RegionManagerSK` | INT64 | SK of `dim_region_manager` on that date. |
| `DirectorSK` | INT64 | SK of `dim_director` on that date. |
| `RegionSKLast` | INT64 | SK of `dim_region_last` (latest assignment structure). |
| `RegionManagerSKLast` | INT64 | SK of the region manager in the latest structure. |
| `DirectorSKLast` | INT64 | SK of the director in the latest structure. |
| `Amt_New` | FLOAT64 | Daily target amount: monthly `CalAmt` divided by the number of non-holiday days of the month (truncated to 10 decimals); 0 on holidays. Summed here. |
| `Qty_New` | FLOAT64 | Daily target quantity, computed the same way from `CalQty`. Summed here. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_target_product_group_mdt.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md).

# Examples

MDT target amount and quantity per month.

```sql
SELECT DATE_TRUNC(Date, MONTH) AS month, SUM(Amt_New) AS target_amt, SUM(Qty_New) AS target_qty
FROM `databuffet-nonprd.fact_view.view_fact_target_product_group_mdt`
GROUP BY month
ORDER BY month
```

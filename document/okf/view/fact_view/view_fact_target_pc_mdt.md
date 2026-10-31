---
type: BigQuery View
title: "view_fact_target_pc_mdt"
description: "One row = one fact_target_saleout_mdt target row (day x branch x marketing group/segment) split evenly across the PCs assigned to the branch and marketing group in that month."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_target_pc_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_target_pc_mdt
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_target_pc_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_target_pc_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Sell-out targets of the modern-trade chains at PC level. [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md) has daily targets per branch and marketing group but no person; [dim_pc](/dimension/dim_pc.md) says which PCs cover a slot in each month. The view divides the target equally among those PCs and keeps every original column of the fact so it can be swapped into a BI model. PcSK identifies employee + branch + marketing group; one employee can have several assignment SKs.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per `fact_target_saleout_mdt` row (target_date, branch_code, marketing_group_id, sub_marketing_id, segment_id) times the number of PCs of its slot in that month; one row with `pc_sk_list` NULL and the full target when no PC is assigned. `dim_pc` is expanded to month level (`GENERATE_DATE_ARRAY` from StartDate to EndDate or 2099-12-31) because targets are daily but assignments monthly; placeholders and `PcSK = -1` are excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `target_date` | DATE | Target day from `fact_target_saleout_mdt` (the monthly target is spread evenly over the days of the month). |
| `store_code` | STRING | Modern-trade chain code. |
| `branch_code` | STRING | Branch code from mds (degenerate, used to trace when `branch_sk = -1`). |
| `branch_sk` | INT64 | SK of `dim_sales_branch_mdt` (`-1` unknown). |
| `zone_sk` | INT64 | ZoneMdtSK of the branch (`-1` unknown). |
| `region_sk` | INT64 | SK of `dim_region` at the target date. |
| `region_manager_sk` | INT64 | SK of `dim_region_manager` at the target date. |
| `director_sk` | INT64 | SK of `dim_director` at the target date. |
| `product_mkt_sk` | INT64 | SK of `dim_product_mkt` for the target's marketing group (`-1` unknown). |
| `marketing_group_id` | STRING | Marketing group id of the target; the key used to match `dim_pc` assignments. |
| `marketing_group_name` | STRING | Marketing group name. |
| `sub_marketing_id` | STRING | Sub-marketing group id of the target row. |
| `sub_marketing_name` | STRING | Sub-marketing group name. |
| `segment_id` | STRING | Segment id of the target row. |
| `segment_name` | STRING | Segment name. |
| `pc_sk_list` | INT64 | Assignment SK of `dim_pc` (PcSK) for employee + branch + marketing group in the target's month (single value despite the name), not a person key; NULL when none is assigned. |
| `target_amt` | FLOAT64 | Target amount for the day divided by the number of PCs in the slot (full amount when no PC), so that the PC rows add back to the fact total. |
| `target_qty` | FLOAT64 | Target quantity divided the same way. |
| `target_year` | INT64 | Year of the target. |
| `target_month` | INT64 | Month of the target. |
| `days_in_month` | INT64 | Number of days the monthly target was spread over; `target_amt * days_in_month` (before the PC split) gives the monthly target. |
| `mds_id` | STRING | MdsID of the target row in mds; kept so the view has the same columns as the fact and can replace it in BI models. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_target_pc_mdt.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_pc](/dimension/dim_pc.md), [fact_table.fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `fact_target_saleout_mdt` (tags `fact_daily` + `saleout_daily`) and `dim_pc` being rebuilt first.

# Examples

Monthly target per PcSK assignment (an employee can appear under several assignment SKs).

```sql
SELECT target_year, target_month, pc_sk_list, SUM(target_amt) AS target_amt, SUM(target_qty) AS target_qty
FROM `databuffet-nonprd.fact_view.view_fact_target_pc_mdt`
WHERE pc_sk_list IS NOT NULL
GROUP BY target_year, target_month, pc_sk_list
ORDER BY target_year, target_month, target_amt DESC
```

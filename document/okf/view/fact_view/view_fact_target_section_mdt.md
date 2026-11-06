---
type: BigQuery View
title: "view_fact_target_section_mdt"
description: "One row = one day x modern-trade chain x marketing group, with the summed sell-out target amount and the number of branches with a target."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_target_section_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_target_section_mdt
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_target_section_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_target_section_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

A small roll-up of [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md) to chain and marketing-group level. It collapses branch, sub-marketing group and segment and keeps only the amount and a branch count.

# Grain and key

One row = one marketing group of one store on one target date: key `target_date`, `store_code`, `marketing_group_id` (unique); `marketing_group_name` is `ANY_VALUE`. Quantity is not included.

# Schema

| Column | Type | Description |
|---|---|---|
| `target_date` | DATE | Target day from `fact_target_saleout_mdt`. |
| `store_code` | STRING | Modern-trade chain code. |
| `marketing_group_id` | STRING | Marketing group id of the target. |
| `marketing_group_name` | STRING | Marketing group name (`ANY_VALUE`, because the name is not in the GROUP BY). |
| `target_amt` | FLOAT64 | Sum of `target_amt` of all branches, sub-marketing groups and segments of the chain and marketing group on that day. |
| `branch_count` | INT64 | Number of distinct `branch_code` values that have a target row for that day, chain and marketing group. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_target_section_mdt.sqlx` (`type: "view"`, tags `view`).
- Reads: [fact_table.fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md).

# Examples

Monthly target per chain and marketing group.

```sql
SELECT DATE_TRUNC(target_date, MONTH) AS month, store_code, marketing_group_id, ANY_VALUE(marketing_group_name) AS marketing_group_name, SUM(target_amt) AS target_amt
FROM `databuffet-nonprd.fact_view.view_fact_target_section_mdt`
GROUP BY month, store_code, marketing_group_id
ORDER BY month, store_code, target_amt DESC
```

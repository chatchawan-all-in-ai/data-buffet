---
type: BigQuery View
title: "view_fact_target_section_mdt"
description: "One row = one day x modern-trade chain x marketing group, with the summed sell-out target amount and the number of branches with a target."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_target_section_mdt&page=table"
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_target_section_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_target_section_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

A small roll-up of [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md) to chain and marketing-group level. It collapses branch, sub-marketing group and segment and keeps only the amount and a branch count, so it is cheap to query for chain-level target dashboards.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per (target_date, store_code, marketing_group_id); `marketing_group_name` is `ANY_VALUE`. Quantity is not included.

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
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `fact_target_saleout_mdt` (tags `fact_daily` + `saleout_daily`) being rebuilt first.

# Examples

Monthly target per chain and marketing group.

```sql
SELECT DATE_TRUNC(target_date, MONTH) AS month, store_code, marketing_group_id, ANY_VALUE(marketing_group_name) AS marketing_group_name, SUM(target_amt) AS target_amt
FROM `databuffet-nonprd.fact_view.view_fact_target_section_mdt`
GROUP BY month, store_code, marketing_group_id
ORDER BY month, store_code, target_amt DESC
```

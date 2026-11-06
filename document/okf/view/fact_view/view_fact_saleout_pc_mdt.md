---
type: BigQuery View
title: "view_fact_saleout_pc_mdt"
description: "One row = one fact_saleout_monthly_mdt sell-out row split evenly across the PCs assigned to its branch and marketing group in that month."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_saleout_pc_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_saleout_pc_mdt
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_saleout_pc_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_saleout_pc_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Sell-out of the modern-trade chains broken down by PC (promoter/product consultant, from [dim_pc](/dimension/dim_pc.md)). [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md) has branch x product sales but no person, while the PC master assigns people to a slot (branch + marketing group, with start/end dates). The view expands each assignment to the months it is valid, divides quantity and amount equally among the PCs of the slot, and flags one row per PcSK assignment per month. One employee may have several assignments across branches or marketing groups.

# Grain and key
One row = one `fact_saleout_monthly_mdt` row for each assigned PC in its slot: key = fact key + `pc_sk_list`. Rows with no assigned PC have `pc_sk_list` NULL; placeholder PCs and `PcSK = -1` are excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `month_date` | DATE | Date of the sell-out row from `fact_saleout_monthly_mdt`; daily for the in-progress month and month-end for closed months. |
| `store_code` | STRING | Modern-trade chain code (e.g. HP, TW, BT, GB, MH, DH) as in `fact_saleout_monthly_mdt`. |
| `branch_code` | STRING | Branch code as sent by the chain (trimmed). |
| `branch_sk` | INT64 | SK of `dim_sales_branch_mdt` (BranchMdtSK); `-1` when the branch is unknown. |
| `zone_sk` | INT64 | ZoneMdtSK of the branch; `-1` when unknown. |
| `sales_channel` | STRING | Sales-channel label from the monthly sell-out feed (pass-through from `fact_saleout_monthly_mdt`). |
| `product_code` | STRING | Chain product code as sent (leading zeros are stripped only when joining to dims). |
| `product_name` | STRING | Product name from the sell-out feed. |
| `product_mdt_sk` | INT64 | SK of `dim_product_mdt`; `-1` when the product is not registered. |
| `product_sk` | INT64 | SK of `dim_product_master`; `-1` when no link. |
| `product_mkt_sk` | INT64 | SK of `dim_product_mkt`; unclassified products fall to the `999 Waiting Master` marketing group (or `-1`). |
| `MarketingGroupID` | STRING | Marketing group id of the product's `dim_product_mkt` row (company ag01); the key used to match `dim_pc` assignments (NULL if the SK has no ag01 row). |
| `report_sk` | INT64 | SK of the `dim_report` line (store + marketing group, falling back to the store's `Other` line, else `-1`). |
| `region_sk` | INT64 | SK of `dim_region` valid at `month_date`. |
| `region_manager_sk` | INT64 | SK of `dim_region_manager` valid at `month_date`. |
| `director_sk` | INT64 | SK of `dim_director` valid at `month_date`. |
| `pc_sk_list` | INT64 | Assignment SK of `dim_pc` (`PcSK`) for an employee, branch and marketing group in that month; NULL when no PC is assigned. |
| `sale_qty` | FLOAT64 | Sell-out quantity divided by the number of PCs sharing the slot (month, branch, marketing group); the full quantity when no PC is assigned. Summing over PCs gives back the original total. |
| `sale_amount` | FLOAT64 | Sell-out amount divided the same way as `sale_qty`. |
| `asatdate` | DATE | Date the source fact was built (`CURRENT_DATE('Asia/Bangkok')` in `fact_saleout_monthly_mdt`). |
| `fact_pc_not_count` | STRING | `No` marks one row per PcSK assignment per month represented in sell-out; `Yes` marks additional rows or rows without an assignment. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_saleout_pc_mdt.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [fact_table.fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [dimension_table.dim_pc](/dimension/dim_pc.md).

# Examples

Sell-out amount per assignment and month.

```sql
SELECT DATE_TRUNC(month_date, MONTH) AS month, pc_sk_list, SUM(sale_amount) AS sale_amount, SUM(sale_qty) AS sale_qty
FROM `databuffet-nonprd.fact_view.view_fact_saleout_pc_mdt`
WHERE pc_sk_list IS NOT NULL
GROUP BY month, pc_sk_list
ORDER BY month, sale_amount DESC
```

Distinct employees represented in sell-out per chain and month (counts people across their assignments).

```sql
SELECT DATE_TRUNC(s.month_date, MONTH) AS month, s.store_code,
       COUNT(DISTINCT pc.EmployeeID) AS pc_with_sales
FROM `databuffet-nonprd.fact_view.view_fact_saleout_pc_mdt` AS s
JOIN `databuffet-nonprd.dimension_table.dim_pc` AS pc
  ON s.pc_sk_list = pc.PcSK
GROUP BY month, s.store_code
ORDER BY month, s.store_code
```

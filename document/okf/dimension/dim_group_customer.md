---
type: BigQuery Table
title: "dim_group_customer"
description: "One row = one customer group (`debgroup`) per company, used to group customers that belong to the same account group."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_group_customer&page=table"
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_group_customer.sqlx"
    title: "Dataform definition (dimension/dim_group_customer.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Customer-group dimension derived from [dim_customer](/dimension/dim_customer.md). Each distinct `debgroup` code per company becomes one row; customers without a group use their own `debcode` as the group, so every customer belongs to exactly one group. It provides `GroupCustomerSK` for the bridge [GroupCustomerSK_CustomerSK](/view/bridge_dataset/GroupCustomerSK_CustomerSK.md), [view_dim_customer](/view/dimension_view/view_dim_customer.md) and the group-level grade table [dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

Used by: [bridge_dataset.GroupCustomerSK_CustomerSK](/view/bridge_dataset/GroupCustomerSK_CustomerSK.md), [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row per (`CompanySK`, `debgroup`) where `debgroup = IFNULL(dim_customer.debgroup, dim_customer.debcode)`. `GroupCustomerSK` is a stable surrogate key (existing group keeps its SK; new groups get `max_sk + ROW_NUMBER()` ordered by `companyID`, `debgroup`).

# Schema

| Column | Type | Description |
|---|---|---|
| `GroupCustomerSK` | INT64 | Stable surrogate key of the customer group; never regenerated. |
| `CompanySK` | INT64 | Company surrogate key from `dim_customer.CompanySK` / [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code of the group. |
| `debgroup` | STRING | Customer group code: `dim_customer.debgroup` (MAC5 `deb.debgroup`), or the customer's own `debcode` when the customer has no group. |

# How it is built

- Definition: `definitions/dimension/dim_group_customer.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: MERGE with stable SK on `GroupCustomerSK` (new groups appended, existing updated; no delete) in a `type: "operations"` file, tag `dimension_daily`. Reads all of `dim_customer` each run (no date window), it runs after `dim_customer`. The target table pre-exists in BigQuery.
- Approximate size (BigQuery metadata, 2026-10-31): 77,551 rows, 2.5 MB.

# Examples

Number of groups and customers per company (group size distribution input).

```sql
SELECT g.companyID, COUNT(DISTINCT g.GroupCustomerSK) AS groups
FROM `databuffet-nonprd.dimension_table.dim_group_customer` AS g
GROUP BY g.companyID;
```

Customers in each multi-customer group (derive the group the same way as the dimension).

```sql
SELECT g.GroupCustomerSK, g.debgroup, COUNT(*) AS customers
FROM `databuffet-nonprd.dimension_table.dim_group_customer` AS g
JOIN `databuffet-nonprd.dimension_table.dim_customer` AS c
  ON c.CompanySK = g.CompanySK AND IFNULL(c.debgroup, c.debcode) = g.debgroup
GROUP BY g.GroupCustomerSK, g.debgroup
HAVING COUNT(*) > 1
ORDER BY customers DESC
LIMIT 20;
```

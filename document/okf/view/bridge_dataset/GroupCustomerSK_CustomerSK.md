---
type: BigQuery View
title: "GroupCustomerSK_CustomerSK"
description: "One row = one (GroupCustomerSK, CustomerSK) pair linking a customer group to a customer, in the bridge_dataset schema."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=bridge_dataset&t=GroupCustomerSK_CustomerSK&page=table"
project_id: databuffet-nonprd
dataset_id: bridge_dataset
table_id: GroupCustomerSK_CustomerSK
tags: ["view", "bridge_dataset"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/bridge_dataset/GroupCustomerSK_CustomerSK.sqlx"
    title: "Dataform definition (view/bridge_dataset/GroupCustomerSK_CustomerSK.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Bridge (many-to-many helper) view between [dim_group_customer](/dimension/dim_group_customer.md) and [dim_customer](/dimension/dim_customer.md). It joins the two on CompanySK and the group code (`debgroup`, or the customer's own `debcode` when it has no group) and keeps only the two surrogate keys, so a BI model can relate group-level and customer-level facts without a direct key. Nothing else in the repo reads it; it is consumed by Power BI.

# Grain and key

One row per distinct (GroupCustomerSK, CustomerSK) (`select distinct`). The join is a FULL JOIN, so a group with no customer yields a row with NULL CustomerSK and a customer with no group yields NULL GroupCustomerSK. A customer without `debgroup` is matched to the group whose code equals its own `debcode`.

# Schema

| Column | Type | Description |
|---|---|---|
| `GroupCustomerSK` | INT64 | SK of the customer group in [dim_group_customer](/dimension/dim_group_customer.md); NULL for customers with no matching group. |
| `CustomerSK` | INT64 | SK of the customer in [dim_customer](/dimension/dim_customer.md); NULL for groups with no matching customer. |

# How it is built

- Definition: `definitions/view/bridge_dataset/GroupCustomerSK_CustomerSK.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_group_customer](/dimension/dim_group_customer.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Dataset `bridge_dataset` (`databuffet.BRIDGE`), not `dimension_view`. Depends on `dim_group_customer` and `dim_customer` being built first (tag `dimension_daily`).

# Examples

Customers that belong to a given group:

```sql
SELECT CustomerSK
FROM `databuffet-nonprd.bridge_dataset.GroupCustomerSK_CustomerSK`
WHERE GroupCustomerSK = 100 AND CustomerSK IS NOT NULL
```

Customer counts per group:

```sql
SELECT GroupCustomerSK, COUNT(DISTINCT CustomerSK) AS customers
FROM `databuffet-nonprd.bridge_dataset.GroupCustomerSK_CustomerSK`
GROUP BY GroupCustomerSK
ORDER BY customers DESC
```

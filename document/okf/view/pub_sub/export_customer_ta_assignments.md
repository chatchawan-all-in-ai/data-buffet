---
type: BigQuery View
title: "export_customer_ta_assignments"
description: "One row = one customer in the portfolio of one TA department for a period, exposed for the Pub/Sub export of the TA app table customer_ta_assignments with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_customer_ta_assignments&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_customer_ta_assignments
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_customer_ta_assignments.sqlx"
    title: "Dataform definition (view/pub_sub/export_customer_ta_assignments.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:27:50+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `customer_ta_assignments`: one row per [org_center_customer_ta](/org_center/org_center_customer_ta.md) row. `company_id` is the customer's company; `department_id` is the TA department that owns the customer; `membership_company_id` is the company paired with `department_id` (the customer's company); NULL when `department_id` is NULL. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-customer_ta_assignments`.

# Grain and key

One row = one customer of one TA department from one start date: key `company_id`, `customer_id`, `department_id`, `valid_from` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company of the customer. Part of the natural key. |
| `customer_id` | STRING | Customer code. Part of the natural key. |
| `department_id` | STRING | TA department (DepartmentID; same value as `zone` in appointments) that owns the customer; NULL when not yet known. Part of the natural key. |
| `share_percent` | FLOAT64 | Share percent from MDS. |
| `valid_from` | DATE | Assignment start. Part of the natural key. |
| `valid_to` | DATE | First day after the assignment (already exclusive in org center); NULL when it never ends. |
| `source_row_id` | STRING | MDS row id. |
| `membership_company_id` | STRING | The company paired with `department_id` (the customer's company); NULL when `department_id` is NULL. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_customer_ta_assignments.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_customer_ta](/org_center/org_center_customer_ta.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_customer_ta_assignments`
GROUP BY row_key
HAVING n > 1
```

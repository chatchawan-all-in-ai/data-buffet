---
type: BigQuery View
title: "export_rls_ta_customer"
description: "One row = one customer access grant of one viewer (employee), exposed for the Pub/Sub export of process_dataset.rls_ta_customer with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_rls_ta_customer&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_rls_ta_customer
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_rls_ta_customer.sqlx"
    title: "Dataform definition (view/pub_sub/export_rls_ta_customer.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:47:32+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [process_dataset.rls_ta_customer](/process/rls_ta_customer.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-rls_ta_customer`.

# Grain and key

One row = one customer access grant of one viewer (employee): key `employee_id`, `customer_company_id`, `customer_code`, `marketing_group_id`, `sub_marketing_id`, `segment_id`, `access_source` (unique); `row_key` is the JSON of that key. `access_source` is part of the key, together with the other 6 columns.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_id` | STRING | The viewer: MDS employee code (the TA app's `person_key`). |
| `customer_company_id` | STRING | Company of the customer and of the mart sales rows (for TA and manager rows also the company of the viewer's seat; for EXCEPTION rows a company in the exception's scope). |
| `customer_code` | STRING | ERP customer code, or `ALL` = every customer of `customer_company_id`. |
| `marketing_group_id` | STRING | `ALL` or a marketing group code (non-`ALL` only on special-access product rows). |
| `sub_marketing_id` | STRING | `ALL` or a marketing sub-group code. |
| `segment_id` | STRING | `ALL` or a segment code. |
| `access_source` | STRING | Where access comes from: `TA` (portfolio customers in the same company for departments where the viewer is seated as TA), `SECTION_MGR`, `REGION_MGR`, `DIRECTOR`, `CEO` (portfolio customers of departments with a TA seated in a unit under the viewer), or `EXCEPTION` (special access). When several apply, the first in this order is kept. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_rls_ta_customer.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [process_dataset.rls_ta_customer](/process/rls_ta_customer.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_rls_ta_customer`
GROUP BY row_key
HAVING n > 1
```

---
type: BigQuery View
title: "export_customer_ta_assignments"
description: "One row = one customer in the portfolio of one TA for a period, with the customer company and the company of the TA membership it points to, exposed for the Pub/Sub export of the TA app table customer_ta_assignments with row_key and row_hash."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-02T20:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `customer_ta_assignments`: one row per [org_center_customer_ta](/org_center/org_center_customer_ta.md) row. `company_id` is the customer's company; `membership_company_id` is the company of the membership the TA already has: the customer's company when the TA has a membership there, otherwise the company of the TA's seat (TA position first, then company_id), e.g. ag01 for ac02 customers served by a TA who sits in ag01. The Cloud Workflow `datamart-publish` compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `customer_ta_assignments` to topic `export-ta-customer_ta_assignments`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One customer of one TA from one start date: key `company_id, customer_id, membership_id, valid_from` (unique). `row_key` is the JSON of the natural key. Rows on 2026-11-02: 20,755 (128 point to another company than the customer).

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company of the customer. Part of the natural key. |
| `customer_id` | STRING | Customer code. Part of the natural key. |
| `membership_id` | STRING | EmployeeID of the TA. Part of the natural key. |
| `share_percent` | FLOAT64 | Share percent from MDS. |
| `valid_from` | DATE | Assignment start. Part of the natural key. |
| `valid_to` | DATE | First day after the assignment (already exclusive in org center); NULL when it never ends. |
| `source_row_id` | STRING | MDS row id. |
| `membership_company_id` | STRING | Company of the TA membership that membership_id points to. |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(<natural key>))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_customer_ta_assignments.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_customer_ta](/org_center/org_center_customer_ta.md), [org_center_member](/org_center/org_center_member.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the org sample sent to the AI team on 2026-11-02 (one file per TA app table).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_customer_ta_assignments`
GROUP BY row_key
HAVING n > 1
```

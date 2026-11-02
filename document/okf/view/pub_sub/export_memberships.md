---
type: BigQuery View
title: "export_memberships"
description: "One row = one person in one company with all seats folded together, exposed for the Pub/Sub export of the TA app table memberships with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_memberships&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_memberships
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_memberships.sqlx"
    title: "Dataform definition (view/pub_sub/export_memberships.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-02T20:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `memberships`: [org_center_member](/org_center/org_center_member.md) seats grouped by company and EmployeeID. `status` is active when the person holds a seat valid today (Asia/Bangkok), else inactive; it changes only when a seat starts or ends. The Cloud Workflow `datamart-publish` compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `memberships` to topic `export-ta-memberships`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One person of one company: key `company_id, employee_id` (unique). `row_key` is the JSON of the natural key. Rows on 2026-11-02: 656 (651 active, 5 inactive).

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code. Part of the natural key. |
| `employee_id` | STRING | MDS EmployeeID. Part of the natural key. |
| `employee_code` | STRING | Same as employee_id. |
| `status` | STRING | active = a seat valid today, otherwise inactive. |
| `status_since` | DATE | Start of the current contiguous seat period when active (overlapping or adjacent seats across all positions and units are merged per company/person); day after the latest completed period when inactive, including gaps before a future seat. NULL before the first seat starts. Independent of lifetime valid_from/valid_to. |
| `valid_from` | DATE | Earliest seat start. |
| `valid_to` | DATE | Last seat end + 1 day; NULL while any seat has no end. |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(<natural key>))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_memberships.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_member](/org_center/org_center_member.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the org sample sent to the AI team on 2026-11-02 (one file per TA app table).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_memberships`
GROUP BY row_key
HAVING n > 1
```

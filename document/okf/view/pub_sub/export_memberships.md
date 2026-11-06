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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `memberships`: [org_center_member](/org_center/org_center_member.md) seats grouped by company and EmployeeID. `status` is active when the person holds a seat valid today (Asia/Bangkok), else inactive. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-memberships`.

# Grain and key

One row = one person of one company: key `company_id`, `employee_id` (unique); `row_key` is the JSON of that key.

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
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_memberships.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_member](/org_center/org_center_member.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_memberships`
GROUP BY row_key
HAVING n > 1
```

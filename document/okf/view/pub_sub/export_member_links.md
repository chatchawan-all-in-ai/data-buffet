---
type: BigQuery View
title: "export_member_links"
description: "One row = one PC to TA department link at one branch from one start date, exposed for the Pub/Sub export of the TA app table member_links with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_member_links&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_member_links
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_member_links.sqlx"
    title: "Dataform definition (view/pub_sub/export_member_links.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `member_links`: one row per [org_center_link](/org_center/org_center_link.md) row (PC_TA links from MDS; the TA side is the department, not the person). pc_type and branch_type are not exported. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-member_links`.

# Grain and key

One row = one link: key `company_id`, `link_type`, `from_membership_id`, `department_id`, `site_id`, `valid_from` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code. Part of the natural key. |
| `link_type` | STRING | PC_TA. Part of the natural key. |
| `from_membership_id` | STRING | EmployeeID of the PC. Part of the natural key. |
| `department_id` | STRING | TA department (DepartmentID; same value as `zone` in appointments) the PC is linked to; NULL when not yet known. Part of the natural key. |
| `site_id` | STRING | Branch code. Part of the natural key. |
| `scope_unit_id` | STRING | No source; always NULL. |
| `valid_from` | DATE | Link start. Part of the natural key. |
| `valid_to` | DATE | First day after the link (already exclusive in org center); NULL when it never ends. |
| `source` | STRING | Constant 'mds'. |
| `source_row_id` | STRING | No source; always NULL. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_member_links.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_link](/org_center/org_center_link.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_member_links`
GROUP BY row_key
HAVING n > 1
```

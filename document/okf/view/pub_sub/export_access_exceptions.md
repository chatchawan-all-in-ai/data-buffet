---
type: BigQuery View
title: "export_access_exceptions"
description: "One row = one special-access scope of a person with the code arrays split to one value per row, exposed for the Pub/Sub export of the TA app table access_exceptions with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_access_exceptions&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_access_exceptions
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_access_exceptions.sqlx"
    title: "Dataform definition (view/pub_sub/export_access_exceptions.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:27:35+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `access_exceptions`: [org_center_exception](/org_center/org_center_exception.md) with director, region and section code arrays split to one value per row (cross product). Rows without an employee_id are kept. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-access_exceptions`.

# Grain and key

One row = one special-access scope: key `source_row_id`, `company_code`, `director_code`, `region_code`, `section_code`, `mkt_group_id`, `mkt_subgroup_id`, `mkt_segment_id` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_id` | STRING | MDS EmployeeID; NULL when MDS has none. |
| `company_code` | STRING | Company code or ALL. Part of the natural key. |
| `report_id` | STRING | No source; always NULL. |
| `report_name` | STRING | No source; always NULL. |
| `director_code` | STRING | Director code or ALL. Part of the natural key. |
| `region_code` | STRING | Region code or ALL. Part of the natural key. |
| `section_code` | STRING | Section code or ALL. Part of the natural key. |
| `department_code` | STRING | No source; always NULL. |
| `mkt_group_id` | STRING | Marketing group or ALL. Part of the natural key. |
| `mkt_subgroup_id` | STRING | Marketing sub-group or ALL. Part of the natural key. |
| `mkt_segment_id` | STRING | Segment or ALL. Part of the natural key. |
| `flag_customer` | BOOL | Customer-level flag from MDS. |
| `source_row_id` | STRING | MDS row id. Part of the natural key. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_access_exceptions.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_exception](/org_center/org_center_exception.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_access_exceptions`
GROUP BY row_key
HAVING n > 1
```

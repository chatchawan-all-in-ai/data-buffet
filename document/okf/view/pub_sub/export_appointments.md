---
type: BigQuery View
title: "export_appointments"
description: "One row = one seat (person, unit, position, start date) with company_id and the TA zone, exposed for the Pub/Sub export of the TA app table appointments with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_appointments&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_appointments
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_appointments.sqlx"
    title: "Dataform definition (view/pub_sub/export_appointments.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:48:25+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `appointments`: one row per [org_center_member](/org_center/org_center_member.md) row. TAs sit at the section; their DepartmentID (zone, เขต) goes in `zone`. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `appointments` to topic `export-ta-appointments`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one seat: key `company_id`, `membership_id`, `org_unit_id`, `position_id`, `valid_from` (unique); `row_key` is the JSON of that key. The key is the uniqueKey of `org_center_member`.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code. Part of the natural key. |
| `membership_id` | STRING | MDS EmployeeID. Part of the natural key. |
| `org_unit_id` | STRING | org_units.id of the same company. Part of the natural key. |
| `position_id` | STRING | positions.code. Part of the natural key. |
| `valid_from` | DATE | Seat start. Part of the natural key. |
| `valid_to` | DATE | First day after the seat (org center end date + 1 day); NULL when it never ends. |
| `is_primary` | BOOL | No source; always NULL. |
| `source` | STRING | Constant 'mds'. |
| `source_row_id` | STRING | No source; always NULL. |
| `zone` | STRING | DepartmentID of a TA seat (several joined by '\|'); NULL on other seats. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_appointments.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_member](/org_center/org_center_member.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the TA app org sample (one file per TA app table).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_appointments`
GROUP BY row_key
HAVING n > 1
```

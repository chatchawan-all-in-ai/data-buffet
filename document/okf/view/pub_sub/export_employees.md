---
type: BigQuery View
title: "export_employees"
description: "One row = one person (EmployeeID): everyone in org_center_person plus the people with a special-access row who have no seat, exposed for the Pub/Sub export of the TA app table employees with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_employees&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_employees
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_employees.sqlx"
    title: "Dataform definition (view/pub_sub/export_employees.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:27:50+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `employees`: people of [org_center_person](/org_center/org_center_person.md) plus the people of [org_center_exception](/org_center/org_center_exception.md) who are not in it. The latter are named from the MDS employee mapping center (first word = first name, the rest = last name; no nickname, no phone, no line_uuid). The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `employees` to topic `export-ta-employees`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one person: key `person_key` (unique); `row_key` is the JSON of that key. `person_key` is the MDS EmployeeID and is never NULL.

# Schema

| Column | Type | Description |
|---|---|---|
| `person_key` | STRING | MDS EmployeeID. Part of the natural key. |
| `display_name` | STRING | Nickname if there is one, otherwise first name. |
| `first_name` | STRING | First name. |
| `last_name` | STRING | Last name. |
| `nickname` | STRING | Nickname; NULL for people named from the mapping center. |
| `email` | STRING | Email from org center / MDS. |
| `phone` | STRING | Mobile phone from MDS employee info; NULL when none. |
| `phone_source` | STRING | 'mds' when phone is set, otherwise NULL. |
| `line_uuid` | STRING | LINE UUID from MDS employee info (org_center_person.line_uuid); NULL for people named from the mapping center or when none. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_employees.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_person](/org_center/org_center_person.md), [org_center_exception](/org_center/org_center_exception.md), `mds_dataset.mds_data_org_employee_mapping_center`.
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the TA app org sample (one file per TA app table).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_employees`
GROUP BY row_key
HAVING n > 1
```

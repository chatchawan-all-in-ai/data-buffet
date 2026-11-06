---
type: BigQuery View
title: "export_dim_calendar"
description: "One row = one calendar day with its weekend and holiday flags, exposed for the Pub/Sub export of dimension_table.dim_calendar with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_calendar&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_calendar
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_calendar.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_calendar.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_calendar](/dimension/dim_calendar.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_calendar`.

# Grain and key

One row = one calendar day with its weekend and holiday flags: key `Date` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `Date` | DATE | Calendar date (key). |
| `Year` | INT64 | Four-digit calendar year (INT64). |
| `MonthNumber` | STRING | Two-digit month number as string (`%m`, '01'-'12'). |
| `MonthShortName` | STRING | Short English month name (`%b`). |
| `MonthOfYear` | STRING | Label `MM-YYYY` (month number, hyphen, four-digit year). |
| `YearMonthNumber` | STRING | Year and month as `YYYYMM` string (`%Y%m`). |
| `WeekendFlag` | STRING | 'Yes' when `DAYOFWEEK = 1` (Sunday), else 'No'; Saturday is not flagged. |
| `HolidayFlag` | STRING | 'Yes' if the date is in `dim_holiday` OR is a weekend, else 'No' (so it is a day-off flag, not holidays only). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_calendar.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_calendar`
GROUP BY row_key
HAVING n > 1
```

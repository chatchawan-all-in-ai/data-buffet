---
type: BigQuery View
title: "view_dim_calendar"
description: "One row = one calendar date, with day/week/month/quarter attributes, holiday flags and the LatestDateFilter flag."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_calendar&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_calendar
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_calendar.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_calendar.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Reporting view over [dim_calendar](/dimension/dim_calendar.md): every dim_calendar column plus the BOOL `LatestDateFilter`, used as the 'latest day' page filter in Power BI models (filters dates, does not aggregate).

# Grain and key

One row per `Date` (same grain as dim_calendar). `LatestDateFilter` is TRUE for dates from the last working day up to yesterday, so normally one row, several after weekends/holidays.

# Schema

| Column | Type | Description |
|---|---|---|
| `Date` | DATE | Calendar date (key). |
| `DayLongName` | STRING | Full English day name (`%A`). |
| `DayShortName` | STRING | Short English day name (`%a`). |
| `MonthLongName` | STRING | Full English month name (`%B`). |
| `MonthNumber` | STRING | Two-digit month number as text ('01'-'12'). |
| `MonthOfYear` | STRING | Text `MM-YYYY`. |
| `MonthShortName` | STRING | Short English month name (`%b`). |
| `QuaterNumber` | STRING | Quarter label 'Q1'-'Q4' (column name is misspelled). |
| `Week` | STRING | Two-digit week number: `EXTRACT(WEEK) + 1`, as text. |
| `WeekendFlag` | STRING | 'Yes' only for Sunday (DayOfWeek 1); Saturday is 'No'. |
| `DayOfWeek` | INT64 | BigQuery day of week, 1 = Sunday ... 7 = Saturday. |
| `Year` | INT64 | Calendar year. |
| `YearMonthNumber` | STRING | Text `YYYYMM`. |
| `YearMonthShort` | STRING | Text `YYYY-Mon` (e.g. 2026-Oct). |
| `YearQuater` | STRING | Text `Qn YYYY` (name misspelled). |
| `Day` | STRING | Two-digit day of month as text. |
| `HolidayFlag` | STRING | 'Yes' for a public holiday (from dim_holiday) or Sunday, else 'No'. Saturday is 'No'. |
| `HolidayNameTH` | STRING | Thai holiday name, or the Thai text for weekend days; derived in dim_calendar. |
| `HolidayNameEN` | STRING | English holiday name, or 'Weekend' for weekend days; derived in dim_calendar. |
| `LongWeekEndFlag` | STRING | 'Yes' when the date is a day off inside a run of 3 or more consecutive days off (weekend/holiday), else 'No'. |
| `LatestDateFilter` | BOOL | BOOL added by this view: TRUE when Date is between the latest working day and yesterday (Asia/Bangkok). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_calendar.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads only dim_calendar (tag `dimension_yearly`, adds new years). Depends on `dim_holiday` being filled for the year to mark holidays.

# Examples

Dates currently selected by the latest-day filter:

```sql
SELECT Date, DayLongName, HolidayFlag
FROM `databuffet-nonprd.dimension_view.view_dim_calendar`
WHERE LatestDateFilter
ORDER BY Date
```

Working days per month for a year:

```sql
SELECT YearMonthNumber, COUNTIF(HolidayFlag = 'No') AS working_days
FROM `databuffet-nonprd.dimension_view.view_dim_calendar`
WHERE Year = 2026
GROUP BY YearMonthNumber
ORDER BY YearMonthNumber
```

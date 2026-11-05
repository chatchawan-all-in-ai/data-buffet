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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Reporting view over [dim_calendar](/dimension/dim_calendar.md): every dim_calendar column plus the BOOL `LatestDateFilter`. No other repo object reads it.

# Grain and key

One row = one calendar date: key `Date` (same grain as dim_calendar). `LatestDateFilter` is TRUE for dates from the latest working day before today up to yesterday; there a working day is a date with `HolidayFlag = 'No'` that is not a Saturday, so Saturday never counts as the latest working day although its `HolidayFlag` is 'No'.

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
| `QuaterNumber` | STRING | Quarter label 'Q1'-'Q4'. |
| `Week` | STRING | Two-digit week number: `EXTRACT(WEEK) + 1`, as text. |
| `WeekendFlag` | STRING | 'Yes' only for Sunday (DayOfWeek 1); Saturday is 'No'. |
| `DayOfWeek` | INT64 | BigQuery day of week, 1 = Sunday ... 7 = Saturday. |
| `Year` | INT64 | Calendar year. |
| `YearMonthNumber` | STRING | Text `YYYYMM`. |
| `YearMonthShort` | STRING | Text `YYYY-Mon` (e.g. 2026-Oct). |
| `YearQuater` | STRING | Text `Qn YYYY`. |
| `Day` | STRING | Two-digit day of month as text. |
| `HolidayFlag` | STRING | 'Yes' for a public holiday (from dim_holiday) or Sunday, else 'No'. Saturday is 'No'. |
| `HolidayNameTH` | STRING | Thai holiday name, or the Thai text for weekend days; derived in dim_calendar. |
| `HolidayNameEN` | STRING | English holiday name, or 'Weekend' for weekend days; derived in dim_calendar. |
| `LongWeekEndFlag` | STRING | 'Yes' when the date is a day off inside a run of 3 or more consecutive days off (weekend/holiday), else 'No'. |
| `LatestDateFilter` | BOOL | BOOL added by this view: TRUE when Date is between the latest working day and yesterday (Asia/Bangkok). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_calendar.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md).

# Examples

Dates selected by the latest-day filter:

```sql
SELECT Date, DayLongName, HolidayFlag
FROM `databuffet-nonprd.dimension_view.view_dim_calendar`
WHERE LatestDateFilter
ORDER BY Date
```

Days with `HolidayFlag = 'No'` (Saturdays included) per month for a year:

```sql
SELECT YearMonthNumber, COUNTIF(HolidayFlag = 'No') AS non_holiday_days
FROM `databuffet-nonprd.dimension_view.view_dim_calendar`
WHERE Year = 2026
GROUP BY YearMonthNumber
ORDER BY YearMonthNumber
```

---
type: BigQuery Table
title: "dim_calendar"
description: "One row = one calendar date with day/week/month/quarter/year labels and weekend, holiday and long-weekend flags."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_calendar&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_calendar
tags: ["dimension", "dimension_yearly"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_calendar.sqlx"
    title: "Dataform definition (dimension/dim_calendar.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Date dimension. It supplies the standard calendar attributes (names, month/quarter/year keys, week number) and Thai business-day flags (weekend, holiday with TH/EN name, long weekend of 3+ consecutive days off) built from [dim_holiday](/dimension/dim_holiday.md).

Read by: [view_dim_calendar](/view/dimension_view/view_dim_calendar.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [dim_customer_grade](/dimension/dim_customer_grade.md), [dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [export_dim_calendar](/view/pub_sub/export_dim_calendar.md).

# Grain and key

One row = one calendar day: key `Date` (natural key; there is no surrogate key column). Each yearly run regenerates dates from 1 January of next year to 31 December of (current year + 2) and replaces those dates; earlier years are kept untouched.

# Schema

| Column | Type | Description |
|---|---|---|
| `Date` | DATE | Calendar date (key). |
| `DayLongName` | STRING | Full English weekday name (`FORMAT_DATE('%A')`), e.g. Monday. |
| `DayShortName` | STRING | Short English weekday name (`%a`). |
| `MonthLongName` | STRING | Full English month name (`%B`). |
| `MonthNumber` | STRING | Two-digit month number as string (`%m`, '01'-'12'). |
| `MonthOfYear` | STRING | Label `MM-YYYY` (month number, hyphen, four-digit year). |
| `MonthShortName` | STRING | Short English month name (`%b`). |
| `QuaterNumber` | STRING | Quarter label `Q1`-`Q4` (column name is spelled `Quater` in the table). |
| `Week` | STRING | Two-digit week string = `EXTRACT(WEEK FROM Date) + 1` (BigQuery WEEK is Sunday-based, week 0 for days before the first Sunday, so values start at 01). |
| `WeekendFlag` | STRING | 'Yes' when `DAYOFWEEK = 1` (Sunday), else 'No'; Saturday is not flagged. |
| `DayOfWeek` | INT64 | BigQuery day of week number, 1 = Sunday ... 7 = Saturday. |
| `Year` | INT64 | Four-digit calendar year (INT64). |
| `YearMonthNumber` | STRING | Year and month as `YYYYMM` string (`%Y%m`). |
| `YearMonthShort` | STRING | Label `YYYY-Mon` (`%Y-%b`), e.g. 2027-Jan. |
| `YearQuater` | STRING | Label `Qn YYYY` (`FORMAT_DATE('Q%Q %Y')`). |
| `Day` | STRING | Two-digit day of month as string (`%d`). |
| `HolidayFlag` | STRING | 'Yes' if the date is in `dim_holiday` OR is a weekend, else 'No' (so it is a day-off flag, not holidays only). |
| `HolidayNameTH` | STRING | Thai holiday name from `dim_holiday` when the date is a listed holiday; 'วันหยุดสุดสัปดาห์' for a weekend day that is not a holiday; 'วันธรรมดา' (normal day) otherwise. |
| `HolidayNameEN` | STRING | English label. For a listed holiday it is the Thai name (`HolidayNameTH`); 'Weekend' for weekend days; 'Normal day' otherwise. |
| `LongWeekEndFlag` | STRING | 'Yes' when the date is a day off (weekend or holiday) inside a run of 3 or more consecutive days off, else 'No'. Runs are counted only within the generated date range. |

# How it is built

- Definition: `definitions/dimension/dim_calendar.sqlx` (`type: "operations"`, tag `dimension_yearly`); the operation owns this table.
- Reads: [dimension_table.dim_holiday](/dimension/dim_holiday.md).
- Yearly `type: "operations"` (tag `dimension_yearly`): builds a TEMP table for next year start through end of current year + 2, then DELETE of matching dates and INSERT (idempotent). Target table pre-exists in BigQuery. Runs after `dim_holiday`.

# Examples

Working days (non-holiday) per month for one year.

```sql
SELECT YearMonthNumber, COUNT(*) AS working_days
FROM `databuffet-nonprd.dimension_table.dim_calendar`
WHERE Year = 2026 AND HolidayFlag = 'No'
GROUP BY YearMonthNumber
ORDER BY YearMonthNumber;
```

Upcoming long weekends and their holiday names.

```sql
SELECT Date, DayLongName, HolidayNameTH
FROM `databuffet-nonprd.dimension_table.dim_calendar`
WHERE LongWeekEndFlag = 'Yes' AND Date >= CURRENT_DATE('Asia/Bangkok')
ORDER BY Date
LIMIT 30;
```

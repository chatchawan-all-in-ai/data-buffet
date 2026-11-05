---
type: BigQuery Table
title: "dim_holiday"
description: "One row = one public holiday date with Thai and English names and a long-weekend flag, from the MDS holiday master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_holiday&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_holiday
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_holiday.sqlx"
    title: "Dataform definition (dimension/dim_holiday.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Holiday calendar master. It has no surrogate key and no company column (holidays are company-neutral). Source: mds `mds_data_holiday_master`.

Read by: [dim_calendar](/dimension/dim_calendar.md).

# Grain and key

One row = one holiday date among active mds rows: key `HolidayDate` (uniqueness is not enforced). No SK and no `uniqueKey`.

# Schema

| Column | Type | Description |
|---|---|---|
| `HolidayDate` | DATE | Date of the holiday (mds `HolidayDate`, DATE passed through). |
| `HolidayNameTH` | STRING | Pass-through of mds `HolidayNameTH`, cleaned with `cleanString` (empty string becomes NULL). Thai holiday name. |
| `HolidayNameEN` | STRING | Pass-through of mds `HolidayNameEN`, cleaned with `cleanString` (empty string becomes NULL). English holiday name. |
| `LongWeekEndFlag` | INT64 | `castInt64` of mds `LongWeekEndFlag`: 1 when the holiday is part of a long weekend, NULL otherwise. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_holiday_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_holiday.sqlx` (`type: "table"`, tags `dimension_daily`).
- Storage options: `{"clusterBy": ["HolidayDate", "LongWeekEndFlag"]}`.
- Reads: `mds_dataset.mds_data_holiday_master` (master data loaded outside this repo).
- Plain SELECT of active mds rows; no surrogate key and no dim_company join.
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); no declared dependencies.

# Examples

Holidays in the current year.

```sql
SELECT HolidayDate, HolidayNameEN, LongWeekEndFlag
FROM `databuffet-nonprd.dimension_table.dim_holiday`
WHERE EXTRACT(YEAR FROM HolidayDate) = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
ORDER BY HolidayDate;
```

Duplicate holiday dates.

```sql
SELECT HolidayDate, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_holiday`
GROUP BY 1
HAVING n > 1;
```

---
type: BigQuery View
title: "export_mds_data_ta_dashboard_display_control"
description: "One row = one row of the MDS dashboard display control (what the TA dashboard shows and in which order), exposed for the Pub/Sub export of mds_dataset.mds_data_ta_dashboard_display_control with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_mds_data_ta_dashboard_display_control&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_mds_data_ta_dashboard_display_control
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_mds_data_ta_dashboard_display_control.sqlx"
    title: "Dataform definition (view/pub_sub/export_mds_data_ta_dashboard_display_control.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of `mds_dataset.mds_data_ta_dashboard_display_control`, for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-mds_data_ta_dashboard_display_control`.

# Grain and key

One row = one row of the MDS dashboard display control (what the TA dashboard shows and in which order): key `companyID`, `ControlKey`, `SectionID`, `ItemType`, `ItemCode` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `companyID` | STRING | Company the row applies to (e.g. ag01). |
| `ControlKey` | STRING | Part of the TA dashboard screen the row controls (PRODUCT_FOCUS, PRODUCT_SERIES, PRODUCT_GROUP_DISPLAY). |
| `SectionID` | STRING | ALL, or the section code the row is limited to. |
| `ItemType` | STRING | Level of ItemCode: MKT_GROUP, SUB_MKT or SERIES. |
| `ItemCode` | STRING | Marketing group code, sub-group code or series name to show. |
| `ItemName` | STRING | Display name of the item. |
| `SortOrder` | FLOAT64 | Order of the item on the screen. |
| `BreakdownBy` | STRING | Breakdown requested for the item (e.g. PUMP_SEGMENT); NULL when none. |
| `StartDate` | DATE | First day the row applies. |
| `EndDate` | DATE | Last day the row applies. |
| `is_active` | BOOL | TRUE while the MDS row is active. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_mds_data_ta_dashboard_display_control.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: `mds_dataset.mds_data_ta_dashboard_display_control`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_mds_data_ta_dashboard_display_control`
GROUP BY row_key
HAVING n > 1
```

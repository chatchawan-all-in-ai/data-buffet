---
type: BigQuery View
title: "export_dim_target_product_group_by_sale_dayofwork"
description: "One row = one daily sales target (amount and quantity) of a sales representative and section for a product marketing group, exposed for the Pub/Sub export of the AI team sample table dimension_table.dim_target_product_group_by_sale_dayofwork with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_target_product_group_by_sale_dayofwork&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_target_product_group_by_sale_dayofwork
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_target_product_group_by_sale_dayofwork.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_target_product_group_by_sale_dayofwork.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:27:50+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `dim_target_product_group_by_sale_dayofwork` to topic `export-ta-dim_target_product_group_by_sale_dayofwork`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one daily sales target (amount and quantity) of a sales representative and section for a product marketing group: key `companyID`, `Date`, `EmployeeID`, `DepartmentID`, `TargetID`, `MarketingGroupID`, `SubMarketingID`, `SegmentID`, `ChannelTargetGroup`, `StartDate` (unique); `row_key` is the JSON of that key. `companyID`, `Date`, `EmployeeID`, `DepartmentID`, `TargetID`, `MarketingGroupID`, `SubMarketingID`, `SegmentID`, `ChannelTargetGroup`, `StartDate` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `Year` | INT64 | Copied: target year (also the join key to the calendar). |
| `Month` | INT64 | Copied: target month. |
| `Day` | STRING | Day of month from dim_calendar (STRING). |
| `SaleRepSKLast` | INT64 | Copied from dim_target_product_group_by_sale: latest-snapshot sales rep SK (dim_sale_representative_last). |
| `SectionSKLast` | INT64 | Copied: latest section SK (dim_section_last). |
| `ProductMktSK` | INT64 | Copied: SK in dim_product_mkt. |
| `CompanySK` | INT64 | Copied: company SK. |
| `Amt_New` | FLOAT64 | Daily target amount = CalAmt / total_day truncated to 10 decimals; 0 on holidays (`HolidayFlag = 'Yes'`). The column to sum for daily targets. |
| `Qty_New` | FLOAT64 | Daily target quantity = CalQty / total_day truncated to 10 decimals; 0 on holidays. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_target_product_group_by_sale_dayofwork.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `dimension_table.dim_target_product_group_by_sale_dayofwork`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_target_product_group_by_sale_dayofwork`
GROUP BY row_key
HAVING n > 1
```

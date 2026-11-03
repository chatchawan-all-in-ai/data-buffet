---
type: BigQuery View
title: "export_view_rls_sale_data"
description: "One row = one row-level-security access level of one user, exposed for the Pub/Sub export of the AI team sample table process_dataset.view_rls_sale_data with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_rls_sale_data&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_rls_sale_data
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_rls_sale_data.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_rls_sale_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [process_dataset.view_rls_sale_data](/view/process_dataset/view_rls_sale_data.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `view_rls_sale_data` to topic `export-ta-view_rls_sale_data`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one row-level-security access level of one user: key `EmployeeEmail`, `LevelName`, `LevelValue` (unique); `row_key` is the JSON of that key. Rows on 2026-11-02: 48,260.

# Schema

| Column | Type | Description |
|---|---|---|
| `EmployeeEmail` | STRING | E-mail of the sales employee from `mds_data_org_employee_mapping_center` (active rows with `employeetype = 'sales'`); the identity matched by Power BI RLS. |
| `LevelName` | STRING | Restricted attribute: `DirectorID`, `RegionID`, `SectionID`, `CompanyID` (from `view_rls_data`) or `CustomerID` (added here). |
| `LevelValue` | STRING | Allowed value for that attribute: an org id, the company report id, or a customer code (`milCus`). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_rls_sale_data.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [process_dataset.view_rls_sale_data](/view/process_dataset/view_rls_sale_data.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `process_dataset.view_rls_sale_data`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_rls_sale_data`
GROUP BY row_key
HAVING n > 1
```

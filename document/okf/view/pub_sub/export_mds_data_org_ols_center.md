---
type: BigQuery View
title: "export_mds_data_org_ols_center"
description: "One row = one user row of the MDS table org_ols_center (access flags for viewing target, cost margin and commission), exposed for the Pub/Sub export of mds_dataset.mds_data_org_ols_center with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_mds_data_org_ols_center&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_mds_data_org_ols_center
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_mds_data_org_ols_center.sqlx"
    title: "Dataform definition (view/pub_sub/export_mds_data_org_ols_center.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of `mds_dataset.mds_data_org_ols_center`, for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-mds_data_org_ols_center`.

# Grain and key

One row = one user row of the MDS table org_ols_center (access flags for viewing target, cost margin and commission): key `employeeemail` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `employeeemail` | STRING | Email address of the user (MDS code of the row); the natural key. |
| `viewtarget` | STRING | Yes when the user may see sales targets on the TA dashboard. |
| `is_active` | BOOL | TRUE while the MDS row is active. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_mds_data_org_ols_center.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: `mds_dataset.mds_data_org_ols_center`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_mds_data_org_ols_center`
GROUP BY row_key
HAVING n > 1
```

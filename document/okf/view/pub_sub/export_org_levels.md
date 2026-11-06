---
type: BigQuery View
title: "export_org_levels"
description: "One row = one org level (depth 1-3: division, region, section) of a company that has units, exposed for the Pub/Sub export of the TA app table org_levels with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_org_levels&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_org_levels
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_org_levels.sqlx"
    title: "Dataform definition (view/pub_sub/export_org_levels.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `org_levels`: one row per company and depth 1 (ฝ่าย), 2 (ภาค) or 3 (ส่วน) that has units in org center. There is no depth 4: TAs sit at the section and carry a zone on appointments. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-org_levels`.

# Grain and key

One row = one company and depth: key `company_id`, `depth` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (e.g. ag01). Part of the natural key. |
| `depth` | INT64 | 1 = division, 2 = region, 3 = section. Part of the natural key. |
| `name` | STRING | Level name shown in the app: ฝ่าย, ภาค or ส่วน. |
| `mds_source_table` | STRING | MDS master the level comes from: mds_data_sales_director_master, mds_data_sales_region_master or mds_data_sales_section_master. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_org_levels.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_unit](/org_center/org_center_unit.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_org_levels`
GROUP BY row_key
HAVING n > 1
```

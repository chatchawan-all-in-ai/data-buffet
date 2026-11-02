---
type: BigQuery View
title: "export_org_units"
description: "One row = one division, region or section of a company (company rows left out), exposed for the Pub/Sub export of the TA app table org_units with region_code, row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_org_units&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_org_units
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_org_units.sqlx"
    title: "Dataform definition (view/pub_sub/export_org_units.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-02T20:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of the TA app table `org_units`: the units of [org_center_unit](/org_center/org_center_unit.md) except the COMPANY rows. `id` is the org center `unit_id`, which is not unique across companies (DIR-00002, REG-PS1-2, SEC-PS1-2 and others exist in ab01 and ag01), so every reference to a unit pairs it with `company_id`. The Cloud Workflow `datamart-publish` compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `org_units` to topic `export-ta-org_units`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One unit of one company: key `company_id, id` (unique). `row_key` is the JSON of the natural key. Rows on 2026-11-02: 164.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Org center `unit_id` (DIR-/REG-/SEC- + code). Part of the natural key together with company_id. |
| `company_id` | STRING | Company code. Part of the natural key. |
| `org_level_id` | INT64 | Depth of the unit (1 division, 2 region, 3 section); points to org_levels.depth of the same company. |
| `parent_unit_id` | STRING | `unit_id` of the parent unit in the same company; NULL for a division (its parent is the company unit, which is not exported). |
| `code` | STRING | `unit_code`: DirectorID, SubRegionID or SectionID. Can repeat across levels. |
| `name` | STRING | `unit_name`. |
| `valid_from` | DATE | Start date of the unit. |
| `valid_to` | DATE | First day after the unit ends (org center end date + 1 day); NULL when it never ends (2066-12-31 in org center). |
| `source_row_id` | STRING | No source; always NULL. |
| `region_code` | STRING | RegionID on region rows (PS1 on PS1-1 to PS1-5); NULL on divisions and sections. |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(<natural key>))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_org_units.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [org_center_unit](/org_center/org_center_unit.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the org sample sent to the AI team on 2026-11-02 (one file per TA app table).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_org_units`
GROUP BY row_key
HAVING n > 1
```

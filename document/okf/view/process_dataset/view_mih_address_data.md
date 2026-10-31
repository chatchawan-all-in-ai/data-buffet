---
type: BigQuery View
title: "view_mih_address_data"
description: "One row = one document (mihType + mihVnos) whose AI-parsed address was matched to a Thai sub-district, district or province, with the geography SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=view_mih_address_data&page=table"
tags: ["view", "process_dataset"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/process_dataset/view_mih_address_data.sqlx"
    title: "Dataform definition (view/process_dataset/view_mih_address_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The document-level twin of [view_deb_address_data](/view/process_dataset/view_deb_address_data.md): it applies the same most-specific-first geography matching (sub-district, then district, then province) to `process_dataset.mih_address_data`, a table of parsed addresses per document header. That table is not built by this repo (it pre-exists in BigQuery), so this view is only useful if it is populated; nothing else in the repo reads it.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per (mihType, mihVnos) of `mih_address_data` that matched at some level, with the same `NOT EXISTS` guards on (mihType, mihVnos); documents that match nothing are absent. There is no company column and no company filter, so the same (type, number) can exist for different companies only if `mih_address_data` carries them.

# Schema

| Column | Type | Description |
|---|---|---|
| `address_type` | STRING | Constant `invoice`. |
| `condition` | STRING | How the address was matched: `sub_districts` (matched to a sub-district), `districts` (only a district matched) or `provinces` (only a province matched). |
| `mihType` | STRING | MAC5 document type of the header (`mih_address_data.mihType`). |
| `mihVnos` | STRING | MAC5 document number of the header (`mih_address_data.mihVnos`); with `mihType` it keys the row. |
| `raw_address` | STRING | Source address text (debtor address lines concatenated) that was sent to the AI parser. |
| `ProvinceSK` | INT64 | SK of `dim_provinces` (Thai province); NULL only if not matched at any level (such rows are not returned). |
| `DistrictSK` | INT64 | SK of `dim_districts`; NULL when matching stopped at province level. |
| `SubDistrictSK` | INT64 | SK of `dim_sub_districts`; NULL when matching stopped at district or province level. |
| `SubDistrictTH` | STRING | Sub-district name in Thai as parsed by the AI (`info.SubDistrictTH`). |
| `SubDistrictEN` | STRING | Sub-district name in English as parsed by the AI. |
| `DistrictTH` | STRING | District name in Thai as parsed by the AI. |
| `DistrictEN` | STRING | District name in English as parsed by the AI. |
| `ProvinceTH` | STRING | Province name in Thai as parsed by the AI. |
| `ProvinceEN` | STRING | Province name in English as parsed by the AI. |

# How it is built

- Definition: `definitions/view/process_dataset/view_mih_address_data.sqlx` (`type: "view"`, tags `view`).
- Reads: `process_dataset.mih_address_data`, `dimension_table.dim_sub_districts`, `dimension_table.dim_districts`, `dimension_table.dim_provinces`.
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; reads `process_dataset.mih_address_data` and the geography dims `dim_provinces/districts/sub_districts`, none of which this repo builds (`dependencies` is empty).

# Examples

Documents per province.

```sql
SELECT ProvinceTH, COUNT(*) AS documents
FROM `databuffet-nonprd.process_dataset.view_mih_address_data`
GROUP BY ProvinceTH
ORDER BY documents DESC
```

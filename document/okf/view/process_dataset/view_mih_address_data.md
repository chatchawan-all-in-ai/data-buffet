---
type: BigQuery View
title: "view_mih_address_data"
description: "One row = one document (mihType + mihVnos) whose AI-parsed address was matched to a Thai sub-district, district or province, with the geography SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=view_mih_address_data&page=table"
project_id: databuffet-nonprd
dataset_id: process_dataset
table_id: view_mih_address_data
tags: ["view", "process_dataset"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/process_dataset/view_mih_address_data.sqlx"
    title: "Dataform definition (view/process_dataset/view_mih_address_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The document-level twin of [view_deb_address_data](/view/process_dataset/view_deb_address_data.md): it applies the same most-specific-first geography matching (sub-district, then district, then province) to `process_dataset.mih_address_data`, a table of parsed addresses per document header. That table is not built by this repo.

No other object in this repo reads it.

# Grain and key

One row = one document address match of `mih_address_data`: intended key `mihType`, `mihVnos` (not unique). `sub_districts`, `districts` and `provinces` rows are chosen most-specific-first with `NOT EXISTS` guards on (`mihType`, `mihVnos`); documents that match nothing are absent. The view has no company column and no company filter, and a name that matches several dimension rows yields several rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `address_type` | STRING | Constant `invoice`. |
| `condition` | STRING | How the address was matched: `sub_districts` (matched to a sub-district), `districts` (only a district matched) or `provinces` (only a province matched). |
| `mihType` | STRING | Document type code of the document header (as in MAC5 `mih`). |
| `mihVnos` | STRING | Document number of the header. |
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
- Type view; no declared dependencies.

# Examples

Documents per province.

```sql
SELECT ProvinceTH, COUNT(*) AS documents
FROM `databuffet-nonprd.process_dataset.view_mih_address_data`
GROUP BY ProvinceTH
ORDER BY documents DESC
```

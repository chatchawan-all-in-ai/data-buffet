---
type: BigQuery View
title: "view_deb_address_data"
description: "One row = one ag01 customer (debcode) whose AI-parsed invoice address was matched to a Thai sub-district, district or province, with the geography SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=view_deb_address_data&page=table"
project_id: databuffet-nonprd
dataset_id: process_dataset
table_id: view_deb_address_data
tags: ["view", "process_dataset"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/process_dataset/view_deb_address_data.sqlx"
    title: "Dataform definition (view/process_dataset/view_deb_address_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Turns the AI-parsed customer addresses of [deb_address_data](/process/deb_address_data.md) (Thai/English sub-district, district and province names from `AI.GENERATE`) into SKs of the geography dimensions (`dim_sub_districts`, `dim_districts`, `dim_provinces`). It tries the most specific match first (sub-district, then district, then province) so each customer gets the deepest SK that could be matched. It is what `fact_transcation`, `Transaction_Data_Mart` and `dim_customer` read for Province/District/SubDistrict SKs.

Used by [onetime.Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md), [fact_table.fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per (company_id, debcode) for company `ag01` that matched at some level: `sub_district` rows first, then `district` rows for customers without a sub-district match, then `province` rows for customers with neither (the `NOT EXISTS` guards). Customers that match nothing are absent (INNER JOINs). The sub-district match uses only the sub-district name when province/district are missing, so a customer could in principle match several sub-districts with the same name.

# Schema

| Column | Type | Description |
|---|---|---|
| `address_type` | STRING | Constant `invoice` (the address is the customer's invoice/debtor address). |
| `condition` | STRING | How the address was matched: `sub_districts` (matched to a sub-district), `districts` (only a district matched) or `provinces` (only a province matched). |
| `company_id` | STRING | Company code from `deb_address_data`; this view keeps only `ag01`. |
| `debcode` | STRING | Customer (debtor) code. |
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

- Definition: `definitions/view/process_dataset/view_deb_address_data.sqlx` (`type: "view"`, tags `view`).
- Reads: [process_dataset.deb_address_data](/process/deb_address_data.md), `dimension_table.dim_sub_districts`, `dimension_table.dim_districts`, `dimension_table.dim_provinces`.
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on the table `process_dataset.deb_address_data` (tag `process`, incremental, AI step gated on CDC changes of `validated_mac5.deb`) and the geography dims `dim_provinces`, `dim_districts`, `dim_sub_districts` (they pre-exist in BigQuery and are not built by this repo). By the dependency rule, tables that read this view (`dim_customer`, `fact_transcation`) declare the table `deb_address_data`, not the view.

# Examples

Customers per province for ag01.

```sql
SELECT ProvinceSK, ProvinceTH, COUNT(*) AS customers
FROM `databuffet-nonprd.process_dataset.view_deb_address_data`
GROUP BY ProvinceSK, ProvinceTH
ORDER BY customers DESC
```

Share of customers matched only at province or district level.

```sql
SELECT condition, COUNT(*) AS customers
FROM `databuffet-nonprd.process_dataset.view_deb_address_data`
GROUP BY condition
```

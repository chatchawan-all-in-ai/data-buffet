---
type: BigQuery View
title: "view_deb_address_data"
description: "One row = one match of the AI-parsed invoice address of an ag01 customer (debcode) to a Thai sub-district, district or province, with the geography SKs."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Turns the AI-parsed customer addresses of [deb_address_data](/process/deb_address_data.md) (Thai/English sub-district, district and province names from `AI.GENERATE`) into SKs of the geography dimensions (`dim_sub_districts`, `dim_districts`, `dim_provinces`). It tries the most specific match first (sub-district, then district, then province) so each customer gets the deepest SK that could be matched.

Read by: [Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md), [dim_customer](/dimension/dim_customer.md), [dim_customer_report_info](/dimension/dim_customer_report_info.md) and [fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row = one customer address match of company `ag01`: intended key `company_id`, `debcode` (not unique). `sub_districts` rows come first, then `districts` rows for customers without a sub-district match, then `provinces` rows for customers with neither (the `NOT EXISTS` guards, on `debcode`). Customers that match nothing are absent (INNER JOINs). The sub-district match falls back to the district and sub-district names, or the sub-district name alone, when the province or district is missing, and the district match uses the district name alone when the province is missing, so one `debcode` can match several dimension rows with the same name.

# Schema

| Column | Type | Description |
|---|---|---|
| `address_type` | STRING | Constant `invoice` (the address is the customer's invoice/debtor address). |
| `condition` | STRING | How the address was matched: `sub_districts` (matched to a sub-district), `districts` (only a district matched) or `provinces` (only a province matched). |
| `company_id` | STRING | Company code from `deb_address_data`; this view keeps only `ag01`. |
| `debcode` | STRING | Customer (debtor) code. |
| `raw_address` | STRING | Source address text (debtor address lines concatenated) that was sent to the AI parser. |
| `ProvinceSK` | INT64 | SK of `dim_provinces` (Thai province); never NULL. |
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

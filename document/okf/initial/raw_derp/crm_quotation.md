---
type: BigQuery Table
title: "crm_quotation"
description: "One row = one record of source table `crm_quotation` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_quotation&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_quotation
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_quotation/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_quotation` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.crm_quotation](/validated/validated_derp/crm_quotation.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `revision_no` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotation_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotation_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `valid_from` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `valid_to` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `pricing_mode` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_1_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_1_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_2_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_2_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_3_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_3_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_path_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_path_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_channel_path_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_master_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_address_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `invoice_account_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `invoice_account_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_account_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_account_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_account_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_account_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_group_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `target_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `target_group_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `price_mode` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_method_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_method_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_method_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_term_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_term_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_term_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_term_other` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_condition_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_condition_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_condition_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_condition_other` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `note_doc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `note_consider` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qt_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `po_ref` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `parent_quotation_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_vat` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dis_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `dis_price_unit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `trade_discount_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `subtotal_before_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `grand_total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_show_project` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_is_vat` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_vat_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_vat_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_vat_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_dis_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_dis_price_unit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_trade_discount_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_subtotal_before_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_vat_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_grand_total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `full_text_search` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ship_range_start` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ship_range_end` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ship_mode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_doc_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_doc_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_doc_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_tax_invoice` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_po` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_customer_do` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_etax` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `address_full` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `address_detail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sub_district_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sub_district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `district_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `province_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `province` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `postal_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `country_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `latitude` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `longitude` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `map_url` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `revamp_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `revamp_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_1_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_1_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_2_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_2_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_active` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `primary_sales_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `primary_sales_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `primary_sales_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_type_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_type_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_type_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `job_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `referrer_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `referrer_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_doc_no_1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_doc_no_2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bu_list` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_bu_list` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_so_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_so_list` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `submitted_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ref_qt_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_invoice_account_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_invoice_account_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_invoice_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_order_account_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_order_account_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_order_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_delivery_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_source` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_change_reason` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_changed_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_changed_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_changed_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_quotation/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_quotation`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_quotation`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

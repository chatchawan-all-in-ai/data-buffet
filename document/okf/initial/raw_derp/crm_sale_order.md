---
type: BigQuery Table
title: "crm_sale_order"
description: "One row = one record of source table `crm_sale_order` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_sale_order&page=table"
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.crm_sale_order](/validated/validated_derp/crm_sale_order.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_draft` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rev_no` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_latest` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `expected_delivery_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `routed_to_credit_approve` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deposit_fully_paid` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotation_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotation_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
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
| `project_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `project_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `target_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `target_group_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
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
| `po_ref` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_vat` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `trade_discount_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `subtotal_before_vat` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `grand_total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deposit_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark_invoice` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark_production` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark_project` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark_project_detail` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark_payment` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remark_payment_bill` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `full_text_search` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `d365_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_active` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_email` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_address_text` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qt_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_group_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_start_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_end_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_mode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_doc_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_doc_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_address_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_address_text` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_delivery_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `site_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `site_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_tax_invoice` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_po` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_customer_do` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_with_etax` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_subdistrict` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_district` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_province` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_postal_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_address_full` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_latitude` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_longitude` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_map_url` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_subdistrict_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_district_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_province_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_delivery_country_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remaining_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `currency_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `wht_base` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `wht_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `wht_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `net_payable` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qt_trade_discount_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_qt_discount_carrier` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `po_expire_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `reference_doc_1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `reference_doc_2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `job_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `referrer_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `referrer_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `primary_sales_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `primary_sales_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `primary_sales_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivery_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sub_contract_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sub_contract_owner_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `paid_total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `outstanding_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `deposit_outstanding_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `next_due_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_invoice_account_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_invoice_account_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_invoice_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_order_account_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_order_account_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_order_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_delivery_address_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `allkonm_order_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `allkonm_sub_order_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_channel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_known_as` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `allkonm_tran_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_creation_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qt_discount_base_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qt_discount_ratio` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_approver_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_requirement_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `doc_requirement_reason` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `po_doc_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `po_doc_status_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `billing_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `po_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_source` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_change_reason` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_changed_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_changed_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_changed_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_sale_order/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_sale_order`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_sale_order`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

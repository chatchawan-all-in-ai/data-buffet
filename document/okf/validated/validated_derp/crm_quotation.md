---
type: BigQuery Table
title: "crm_quotation"
description: "One row = one cleaned copy of the source table `crm_quotation`, unique on (quotation_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_quotation&page=table"
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_quotation.sqlx"
    title: "Dataform definition (validated/derp/crm_quotation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_quotation`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `quotation_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_id` | STRING | Meaning not documented in the repo. |
| `revision_no` | INT64 | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `quotation_no` | STRING | Meaning not documented in the repo. |
| `quotation_date` | DATE | Meaning not documented in the repo. |
| `valid_from` | DATETIME | Meaning not documented in the repo. |
| `valid_to` | DATETIME | Meaning not documented in the repo. |
| `pricing_mode` | INT64 | Meaning not documented in the repo. |
| `sale_channel_1_id` | STRING | Meaning not documented in the repo. |
| `sale_channel_1_code` | STRING | Meaning not documented in the repo. |
| `sale_channel_2_id` | STRING | Meaning not documented in the repo. |
| `sale_channel_2_code` | STRING | Meaning not documented in the repo. |
| `sale_channel_3_id` | STRING | Meaning not documented in the repo. |
| `sale_channel_3_code` | STRING | Meaning not documented in the repo. |
| `sale_channel_path_id` | STRING | Meaning not documented in the repo. |
| `sale_channel_path_code` | STRING | Meaning not documented in the repo. |
| `sale_channel_path_name` | STRING | Meaning not documented in the repo. |
| `customer_master_id` | STRING | Meaning not documented in the repo. |
| `customer_code` | STRING | Meaning not documented in the repo. |
| `customer_address_id` | STRING | Meaning not documented in the repo. |
| `customer_address_code` | STRING | Meaning not documented in the repo. |
| `invoice_account_id` | STRING | Meaning not documented in the repo. |
| `invoice_account_code` | STRING | Meaning not documented in the repo. |
| `order_account_id` | STRING | Meaning not documented in the repo. |
| `order_account_code` | STRING | Meaning not documented in the repo. |
| `delivery_account_id` | STRING | Meaning not documented in the repo. |
| `delivery_account_code` | STRING | Meaning not documented in the repo. |
| `customer_group_id` | STRING | Meaning not documented in the repo. |
| `customer_group_code` | STRING | Meaning not documented in the repo. |
| `project_id` | STRING | Meaning not documented in the repo. |
| `project_code` | STRING | Meaning not documented in the repo. |
| `target_group_id` | STRING | Meaning not documented in the repo. |
| `target_group_code` | STRING | Meaning not documented in the repo. |
| `price_mode` | INT64 | Meaning not documented in the repo. |
| `payment_method_id` | STRING | Meaning not documented in the repo. |
| `payment_method_code` | STRING | Meaning not documented in the repo. |
| `payment_method_name` | STRING | Meaning not documented in the repo. |
| `payment_term_id` | STRING | Meaning not documented in the repo. |
| `payment_term_code` | STRING | Meaning not documented in the repo. |
| `payment_term_name` | STRING | Meaning not documented in the repo. |
| `payment_term_other` | STRING | Meaning not documented in the repo. |
| `payment_condition_id` | STRING | Meaning not documented in the repo. |
| `payment_condition_code` | STRING | Meaning not documented in the repo. |
| `payment_condition_name` | STRING | Meaning not documented in the repo. |
| `payment_condition_other` | STRING | Meaning not documented in the repo. |
| `note_doc` | STRING | Meaning not documented in the repo. |
| `note_consider` | STRING | Meaning not documented in the repo. |
| `qt_type` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `po_ref` | STRING | Meaning not documented in the repo. |
| `parent_quotation_no` | STRING | Meaning not documented in the repo. |
| `is_vat` | INT64 | Meaning not documented in the repo. |
| `vat_code` | STRING | Meaning not documented in the repo. |
| `vat_name` | STRING | Meaning not documented in the repo. |
| `vat_rate` | FLOAT64 | Meaning not documented in the repo. |
| `dis_price` | FLOAT64 | Meaning not documented in the repo. |
| `dis_price_unit` | STRING | Meaning not documented in the repo. |
| `total_amount` | FLOAT64 | Meaning not documented in the repo. |
| `trade_discount_amount` | FLOAT64 | Meaning not documented in the repo. |
| `subtotal_before_vat` | FLOAT64 | Meaning not documented in the repo. |
| `vat_amount` | FLOAT64 | Meaning not documented in the repo. |
| `grand_total_amount` | FLOAT64 | Meaning not documented in the repo. |
| `is_show_project` | BOOL | Meaning not documented in the repo. |
| `project_is_vat` | INT64 | Meaning not documented in the repo. |
| `project_vat_code` | STRING | Meaning not documented in the repo. |
| `project_vat_name` | STRING | Meaning not documented in the repo. |
| `project_vat_rate` | FLOAT64 | Meaning not documented in the repo. |
| `project_dis_price` | FLOAT64 | Meaning not documented in the repo. |
| `project_dis_price_unit` | STRING | Meaning not documented in the repo. |
| `project_total_amount` | FLOAT64 | Meaning not documented in the repo. |
| `project_trade_discount_amount` | FLOAT64 | Meaning not documented in the repo. |
| `project_subtotal_before_vat` | FLOAT64 | Meaning not documented in the repo. |
| `project_vat_amount` | FLOAT64 | Meaning not documented in the repo. |
| `project_grand_total_amount` | FLOAT64 | Meaning not documented in the repo. |
| `full_text_search` | STRING | Meaning not documented in the repo. |
| `ship_range_start` | DATETIME | Meaning not documented in the repo. |
| `ship_range_end` | DATETIME | Meaning not documented in the repo. |
| `ship_mode` | STRING | Meaning not documented in the repo. |
| `delivery_doc_id` | STRING | Meaning not documented in the repo. |
| `delivery_doc_code` | STRING | Meaning not documented in the repo. |
| `delivery_doc_name` | STRING | Meaning not documented in the repo. |
| `doc_with_tax_invoice` | BOOL | Meaning not documented in the repo. |
| `doc_with_po` | BOOL | Meaning not documented in the repo. |
| `doc_with_customer_do` | BOOL | Meaning not documented in the repo. |
| `doc_with_etax` | BOOL | Meaning not documented in the repo. |
| `address_full` | STRING | Meaning not documented in the repo. |
| `address_detail` | STRING | Meaning not documented in the repo. |
| `sub_district_code` | STRING | Meaning not documented in the repo. |
| `sub_district` | STRING | Meaning not documented in the repo. |
| `district_code` | STRING | Meaning not documented in the repo. |
| `district` | STRING | Meaning not documented in the repo. |
| `province_code` | STRING | Meaning not documented in the repo. |
| `province` | STRING | Meaning not documented in the repo. |
| `postal_code` | STRING | Meaning not documented in the repo. |
| `country_code` | STRING | Meaning not documented in the repo. |
| `latitude` | FLOAT64 | Meaning not documented in the repo. |
| `longitude` | FLOAT64 | Meaning not documented in the repo. |
| `map_url` | STRING | Meaning not documented in the repo. |
| `mac5_id` | INT64 | Meaning not documented in the repo. |
| `mac5_code` | STRING | Meaning not documented in the repo. |
| `revamp_id` | INT64 | Meaning not documented in the repo. |
| `revamp_code` | STRING | Meaning not documented in the repo. |
| `d365_id` | INT64 | Meaning not documented in the repo. |
| `d365_code` | STRING | Meaning not documented in the repo. |
| `ref_1_id` | INT64 | Meaning not documented in the repo. |
| `ref_1_code` | STRING | Meaning not documented in the repo. |
| `ref_2_id` | INT64 | Meaning not documented in the repo. |
| `ref_2_code` | STRING | Meaning not documented in the repo. |
| `is_active` | BOOL | Active flag from the source (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `updated_by_name` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `primary_sales_id` | STRING | Meaning not documented in the repo. |
| `primary_sales_code` | STRING | Meaning not documented in the repo. |
| `primary_sales_name` | STRING | Meaning not documented in the repo. |
| `order_type_id` | STRING | Meaning not documented in the repo. |
| `order_type_code` | STRING | Meaning not documented in the repo. |
| `order_type_name` | STRING | Meaning not documented in the repo. |
| `job_code` | STRING | Meaning not documented in the repo. |
| `referrer_code` | STRING | Meaning not documented in the repo. |
| `referrer_name` | STRING | Meaning not documented in the repo. |
| `ref_doc_no_1` | STRING | Meaning not documented in the repo. |
| `ref_doc_no_2` | STRING | Meaning not documented in the repo. |
| `bu_list` | STRING | Meaning not documented in the repo. |
| `project_bu_list` | STRING | Meaning not documented in the repo. |
| `so_status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `ref_so_no` | STRING | Meaning not documented in the repo. |
| `ref_so_list` | STRING | Meaning not documented in the repo. |
| `submitted_at` | DATETIME | Meaning not documented in the repo. |
| `ref_qt_no` | STRING | Meaning not documented in the repo. |
| `customer_invoice_account_id` | STRING | Meaning not documented in the repo. |
| `customer_invoice_account_code` | STRING | Meaning not documented in the repo. |
| `customer_invoice_address_id` | STRING | Meaning not documented in the repo. |
| `customer_order_account_id` | STRING | Meaning not documented in the repo. |
| `customer_order_account_code` | STRING | Meaning not documented in the repo. |
| `customer_order_address_id` | STRING | Meaning not documented in the repo. |
| `customer_delivery_address_id` | STRING | Meaning not documented in the repo. |
| `payment_type` | STRING | Meaning not documented in the repo. |
| `vat_source` | STRING | Meaning not documented in the repo. |
| `vat_change_reason` | STRING | Meaning not documented in the repo. |
| `vat_changed_by` | STRING | Meaning not documented in the repo. |
| `vat_changed_by_name` | STRING | Meaning not documented in the repo. |
| `vat_changed_at` | DATETIME | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_quotation.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_quotation](/initial/raw_derp/crm_quotation.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `quotation_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,820 rows, 4.5 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_quotation`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT quotation_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_quotation`
GROUP BY quotation_id
HAVING n > 1
```

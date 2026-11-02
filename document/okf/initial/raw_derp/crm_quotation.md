---
type: BigQuery Table
title: "crm_quotation"
description: "One row = one quotation (latest revision), a record of source table `crm_quotation` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_quotation/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_quotation` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Sales quotation headers of the DERP CRM: customer and accounts, sales channel, payment terms, amounts and VAT, approval and sales-order status. Used by: [validated_derp.crm_quotation](/validated/validated_derp/crm_quotation.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_id` | STRING | UUID of the quotation. |
| `revision_no` | INT64 | Revision number of the quotation (0 = original, incremented on each revision). |
| `status` | STRING | Quotation status (`QT_DRAFT`, `QT_WAIT_MGR`, `QT_WAIT_BIZ`, `QT_APPROVED`, `QT_REJECT_MGR`, `QT_REJECT_BIZ`, `QT_CANCELLED`). |
| `quotation_no` | STRING | Quotation document number (e.g. `QT2607...` or `MDT2610...`). |
| `quotation_date` | STRING | Quotation document date. |
| `valid_from` | STRING | Start of the quotation validity period. |
| `valid_to` | STRING | End of the quotation validity period. |
| `pricing_mode` | INT64 | Pricing mode code of the quotation (`0` or `1`). |
| `sale_channel_1_id` | STRING | UUID of the level-1 sales channel in `sales_channel_master_sales_channel`. |
| `sale_channel_1_code` | STRING | Code of the level-1 sales channel (e.g. `MDT`, `PS1`, `A`). |
| `sale_channel_2_id` | STRING | UUID of the level-2 sales channel. |
| `sale_channel_2_code` | STRING | Code of the level-2 sales channel. |
| `sale_channel_3_id` | STRING | UUID of the level-3 sales channel. |
| `sale_channel_3_code` | STRING | Code of the level-3 sales channel. |
| `sale_channel_path_id` | STRING | Chain of sales-channel UUIDs of the quotation, separated by `/`. |
| `sale_channel_path_code` | STRING | Chain of sales-channel codes of the quotation, separated by `/` (e.g. `MDT/`). |
| `sale_channel_path_name` | STRING | Chain of sales-channel names of the quotation. |
| `customer_master_id` | STRING | UUID of the customer in `crm_customer_master`. |
| `customer_code` | STRING | Customer code in the CRM (e.g. `C0000136`; `NCT...` for new customers). |
| `customer_address_id` | STRING | UUID of the customer address in `crm_customer_address` used on the quotation. |
| `customer_address_code` | STRING | Customer code of the address account used on the quotation. |
| `invoice_account_id` | STRING | UUID of the invoice (bill-to) address. |
| `invoice_account_code` | STRING | Customer code of the invoice (bill-to) account. |
| `order_account_id` | STRING | UUID of the order account address. |
| `order_account_code` | STRING | Customer code of the order account. |
| `delivery_account_id` | STRING | UUID of the delivery (ship-to) address. |
| `delivery_account_code` | STRING | Customer code of the delivery (ship-to) account. |
| `customer_group_id` | STRING | UUID of the customer group of the quotation. |
| `customer_group_code` | STRING | Customer group code of the quotation (e.g. `PS`, `BT`, `DH`, `HP`). |
| `project_id` | STRING | UUID of the project the quotation belongs to. |
| `project_code` | STRING | Project code (e.g. `PRJ0002`). |
| `target_group_id` | STRING | UUID of the target customer group of the quotation. |
| `target_group_code` | STRING | Target customer group code (e.g. `TT`, `DD`, `DA`, `DT`, `DC`). |
| `price_mode` | INT64 | Price mode code of the quotation (`0` or `1`). |
| `payment_method_id` | STRING | UUID of the payment method. |
| `payment_method_code` | STRING | Payment method code (`CASH`, `BANK_TRANSFER`). |
| `payment_method_name` | STRING | Payment method name. |
| `payment_term_id` | STRING | UUID of the payment term. |
| `payment_term_code` | STRING | Payment term code (e.g. `N000` = cash). |
| `payment_term_name` | STRING | Payment term name. |
| `payment_term_other` | STRING | Free-text payment term when no standard term applies. |
| `payment_condition_id` | STRING | UUID of the payment condition. |
| `payment_condition_code` | STRING | Payment condition code (e.g. `CASH_100_BFR` = 100% cash before delivery). |
| `payment_condition_name` | STRING | Payment condition name. |
| `payment_condition_other` | STRING | Free-text payment condition when no standard condition applies. |
| `note_doc` | STRING | Note printed on the quotation document. |
| `note_consider` | STRING | Note for the approver's consideration. |
| `qt_type` | STRING | Quotation type (`QT` = standard quotation, `MDT` = MDT channel quotation). |
| `po_ref` | STRING | Customer purchase-order reference. |
| `parent_quotation_no` | STRING | Quotation number of the parent quotation. |
| `is_vat` | INT64 | VAT flag of the quotation (`0` or `1`). |
| `vat_code` | STRING | VAT code (e.g. `V07`, `VAT7`). |
| `vat_name` | STRING | VAT code name. |
| `vat_rate` | FLOAT64 | VAT rate in percent (e.g. 7). |
| `dis_price` | FLOAT64 | Bill-level discount value entered on the quotation, in the unit given by `dis_price_unit`. |
| `dis_price_unit` | STRING | Unit of the bill-level discount (e.g. `BAHT`). |
| `total_amount` | FLOAT64 | Total of the quotation lines before bill-level discount and VAT, in THB. |
| `trade_discount_amount` | FLOAT64 | Bill-level trade discount amount, in THB. |
| `subtotal_before_vat` | FLOAT64 | Amount after trade discount and before VAT, in THB. |
| `vat_amount` | FLOAT64 | VAT amount, in THB. |
| `grand_total_amount` | FLOAT64 | Grand total including VAT, in THB. |
| `is_show_project` | BOOL | Flag showing the project price set is shown on the quotation. |
| `project_is_vat` | INT64 | Project price set: VAT flag of the quotation (`0` or `1`). |
| `project_vat_code` | STRING | Project price set: VAT code (e.g. `V07`, `VAT7`). |
| `project_vat_name` | STRING | Project price set: VAT code name. |
| `project_vat_rate` | FLOAT64 | Project price set: VAT rate in percent (e.g. 7). |
| `project_dis_price` | FLOAT64 | Project price set: bill-level discount value entered on the quotation, in the unit given by `dis_price_unit`. |
| `project_dis_price_unit` | STRING | Project price set: unit of the bill-level discount (e.g. `BAHT`). |
| `project_total_amount` | FLOAT64 | Project price set: total of the quotation lines before bill-level discount and VAT, in THB. |
| `project_trade_discount_amount` | FLOAT64 | Project price set: bill-level trade discount amount, in THB. |
| `project_subtotal_before_vat` | FLOAT64 | Project price set: amount after trade discount and before VAT, in THB. |
| `project_vat_amount` | FLOAT64 | Project price set: VAT amount, in THB. |
| `project_grand_total_amount` | FLOAT64 | Project price set: grand total including VAT, in THB. |
| `full_text_search` | STRING | Concatenated text of the quotation's numbers and names used for full-text search. |
| `ship_range_start` | STRING | Start of the requested shipping date range. |
| `ship_range_end` | STRING | End of the requested shipping date range. |
| `ship_mode` | STRING | Shipping mode of the quotation. |
| `delivery_doc_id` | STRING | UUID of the delivery document type. |
| `delivery_doc_code` | STRING | Code of the delivery document type. |
| `delivery_doc_name` | STRING | Name of the delivery document type. |
| `doc_with_tax_invoice` | BOOL | Flag showing a tax invoice must accompany the delivery. |
| `doc_with_po` | BOOL | Flag showing the customer purchase order must accompany the delivery. |
| `doc_with_customer_do` | BOOL | Flag showing the customer's delivery order must accompany the delivery. |
| `doc_with_etax` | BOOL | Flag showing an e-Tax invoice is issued. |
| `address_full` | STRING | Full delivery address of the quotation as one text string. |
| `address_detail` | STRING | Delivery address detail line of the quotation. |
| `sub_district_code` | STRING | Sub-district code (6-digit Thai administrative code). |
| `sub_district` | STRING | Sub-district (tambon or khwaeng) name. |
| `district_code` | STRING | District code (4-digit Thai administrative code). |
| `district` | STRING | District (amphoe or khet) name. |
| `province_code` | STRING | Province code (2-digit Thai administrative code). |
| `province` | STRING | Province name. |
| `postal_code` | STRING | Postal code. |
| `country_code` | STRING | Country code (ISO 3166 alpha-3, e.g. `THA`). |
| `latitude` | FLOAT64 | Latitude of the location in decimal degrees. |
| `longitude` | FLOAT64 | Longitude of the location in decimal degrees. |
| `map_url` | STRING | Map link (e.g. Google Maps URL) of the location. |
| `mac5_id` | INT64 | Numeric ID of the quotation in MAC5. |
| `mac5_code` | STRING | Document code of the quotation in MAC5. |
| `revamp_id` | INT64 | Numeric ID of the quotation in the Revamp system. |
| `revamp_code` | STRING | Document code of the quotation in the Revamp system. |
| `d365_id` | INT64 | Numeric ID of the quotation in D365. |
| `d365_code` | STRING | Document code of the quotation in D365. |
| `ref_1_id` | INT64 | Numeric ID of the quotation in reference system 1. |
| `ref_1_code` | STRING | Document code of the quotation in reference system 1. |
| `ref_2_id` | INT64 | Numeric ID of the quotation in reference system 2. |
| `ref_2_code` | STRING | Document code of the quotation in reference system 2. |
| `is_active` | BOOL | Flag showing the quotation is active. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `primary_sales_id` | STRING | UUID of the primary salesperson of the quotation. |
| `primary_sales_code` | STRING | Employee number of the primary salesperson. |
| `primary_sales_name` | STRING | Name of the primary salesperson. |
| `order_type_id` | STRING | UUID of the order type. |
| `order_type_code` | STRING | Order type code. |
| `order_type_name` | STRING | Order type name. |
| `job_code` | STRING | Job code of the quotation. |
| `referrer_code` | STRING | Code of the referrer of the sale. |
| `referrer_name` | STRING | Name of the referrer of the sale. |
| `ref_doc_no_1` | STRING | First external reference document number. |
| `ref_doc_no_2` | STRING | Second external reference document number. |
| `bu_list` | STRING | JSON array of the business units (`bu_code`, `bu_name`) on the quotation lines. |
| `project_bu_list` | STRING | JSON array of the business units (`bu_code`, `bu_name`) on the project price set. |
| `so_status` | STRING | Sales-order status of the quotation (`NOT_APPROVED`, `PENDING`, `SO_DRAFT`, `SO_PARTIAL`, `SO_CREATED`). |
| `ref_so_no` | STRING | Sales order number created from the quotation. |
| `ref_so_list` | STRING | JSON array of sales orders created from the quotation. |
| `submitted_at` | STRING | Timestamp when the quotation was submitted for approval. |
| `ref_qt_no` | STRING | Quotation number this quotation references. |
| `customer_invoice_account_id` | STRING | UUID of the invoice (bill-to) customer in `crm_customer_master`. |
| `customer_invoice_account_code` | STRING | Customer code of the invoice (bill-to) customer. |
| `customer_invoice_address_id` | STRING | UUID of the invoice address in `crm_customer_address`. |
| `customer_order_account_id` | STRING | UUID of the ordering customer in `crm_customer_master`. |
| `customer_order_account_code` | STRING | Customer code of the ordering customer. |
| `customer_order_address_id` | STRING | UUID of the ordering customer's address in `crm_customer_address`. |
| `customer_delivery_address_id` | STRING | UUID of the delivery address in `crm_customer_address`. |
| `payment_type` | STRING | Payment type (e.g. `CASH`). |
| `vat_source` | STRING | Source the VAT setting was taken from. |
| `vat_change_reason` | STRING | Reason given when the VAT setting was changed. |
| `vat_changed_by` | STRING | Identifier of the user who changed the VAT setting. |
| `vat_changed_by_name` | STRING | Display name of the user who changed the VAT setting. |
| `vat_changed_at` | STRING | Timestamp when the VAT setting was changed. |
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

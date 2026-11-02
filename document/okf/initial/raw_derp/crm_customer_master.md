---
type: BigQuery Table
title: "crm_customer_master"
description: "One row = one customer, a record of source table `crm_customer_master` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_customer_master&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_customer_master
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_customer_master/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_customer_master` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Customer master records of the DERP CRM: codes (CRM, MAC5, ERP party), names, tax ID, accounts, tax and currency settings, and approval status. Used by: [validated_derp.crm_customer_master](/validated/validated_derp/crm_customer_master.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_master_id` | STRING | UUID of the customer master record. |
| `customer_code` | STRING | Customer code in the CRM (e.g. `C0000136`; `NCT...` for new customers). |
| `mac5_code` | STRING | Customer code in MAC5 (9-digit customer number). |
| `d365_party_id` | STRING | Party ID of the customer in the ERP (Dynamics 365). |
| `party_type` | STRING | Party type (`Organization` or `Person`). |
| `party_type_raw` | STRING | Party type as received from the source system. |
| `tax_id` | STRING | Tax identification number (13 digits). |
| `organization_name_th` | STRING | Organization name in Thai. |
| `organization_name_en` | STRING | Organization name in English. |
| `short_name_th` | STRING | Short name in Thai. |
| `short_name_en` | STRING | Short name in English. |
| `acronym_th` | STRING | Acronym in Thai. |
| `acronym_en` | STRING | Acronym in English. |
| `search_name` | STRING | Search name of the customer. |
| `prefix_name` | STRING | Name prefix (title) of a person customer. |
| `first_name_th` | STRING | First name in Thai (person customers). |
| `last_name_th` | STRING | Last name in Thai (person customers). |
| `middle_name_th` | STRING | Middle name in Thai (person customers). |
| `first_name_en` | STRING | First name in English (person customers). |
| `last_name_en` | STRING | Last name in English (person customers). |
| `middle_name_en` | STRING | Middle name in English (person customers). |
| `branch_code` | STRING | Branch code of the customer for tax invoices. |
| `branch_name` | STRING | Branch name of the customer for tax invoices. |
| `is_one_time` | BOOL | Flag marking a one-time customer. |
| `invoice_account` | STRING | Customer code of the invoice (bill-to) account. |
| `order_account` | STRING | Customer code of the order account. |
| `delivery_account` | STRING | Customer code of the delivery (ship-to) account. |
| `withholding_tax_code` | STRING | Withholding tax code (e.g. `WHTAR`). |
| `withholding_tax_rate` | FLOAT64 | Withholding tax rate in percent. |
| `vat_code` | STRING | VAT code of the customer. |
| `vat_rate` | FLOAT64 | VAT rate in percent (e.g. 7). |
| `sales_tax_group` | STRING | Sales tax group (`DOM` = domestic, `OVS` = overseas). |
| `currency` | STRING | Currency code (e.g. `THB`). |
| `language` | STRING | Language code of the customer (e.g. `th`, `en-US`). |
| `website` | STRING | Customer website URL. |
| `grade` | STRING | Customer grade. |
| `book3_color` | STRING | Book-3 color classification of the customer. |
| `store_code` | STRING | Store code of the customer. |
| `store_name` | STRING | Store name of the customer. |
| `sales_remark` | STRING | Remark from the sales team. |
| `account_remark` | STRING | Remark from the accounting team. |
| `marketing_remark` | STRING | Remark from the marketing team. |
| `status` | STRING | Customer approval status (e.g. `CUST_APPROVED`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `full_text_search` | STRING | Concatenated text of the customer's codes and names used for full-text search. |
| `is_new_customer` | BOOL | Flag marking a customer newly created in the CRM. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Flag set when the record has been synchronized with the ERP (true for migrated customers, false for records created only in the CRM). |
| `require_po` | BOOL | Flag showing the customer requires a purchase order on sales. |
| `customer_known_as` | STRING | Alias or code the customer is known by. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_customer_master/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_customer_master`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_customer_master`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

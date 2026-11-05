---
type: BigQuery Table
title: "crm_customer_master"
description: "One row = one customer from source table `crm_customer_master`, unique on (customer_master_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_master&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_master
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_master.sqlx"
    title: "Dataform definition (validated/derp/crm_customer_master.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_customer_master`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Customer master records of the DERP CRM: codes (CRM, MAC5, ERP party), names, tax ID, accounts, tax and currency settings, and approval status.
No other repo object reads it.

# Grain and key

One row per `customer_master_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `full_text_search` | STRING | Concatenated text of the customer's codes and names used for full-text search. |
| `is_new_customer` | BOOL | Flag marking a customer newly created in the CRM. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Flag set when the record has been synchronized with the ERP (true for migrated customers, false for records created only in the CRM). |
| `require_po` | BOOL | Flag showing the customer requires a purchase order on sales. |
| `customer_known_as` | STRING | Alias or code the customer is known by. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_master.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_master](/initial/raw_derp/crm_customer_master.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_master_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_master`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT customer_master_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_customer_master`
GROUP BY customer_master_id
HAVING n > 1
```

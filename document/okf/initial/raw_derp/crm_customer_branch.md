---
type: BigQuery Table
title: "crm_customer_branch"
description: "One row = one customer branch, a record of source table `crm_customer_branch` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_customer_branch&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_customer_branch
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (definitions/initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:codex/gpt-6", at: "2026-11-09T15:45:18+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_customer_branch/*` (Hive-partitioned by `ASATDATE`). It is the raw landing copy of the `crm_customer_branch` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Customer branch details, including contact, address and delivery information.

Read by: [validated_derp.crm_customer_branch](/validated/validated_derp/crm_customer_branch.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; see the [validated table card](/validated/validated_derp/crm_customer_branch.md#how-it-is-built) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_branch_id` | STRING | Source identifier of the customer-branch record. |
| `customer_master_id` | STRING | Identifier of the customer record. |
| `customer_code` | STRING | Customer code from CRM. |
| `branch_code` | STRING | Code assigned to the customer branch. |
| `branch_name` | STRING | Customer branch name. |
| `branch_name_en` | STRING | Customer branch name in English. |
| `branch_type` | STRING | Type of customer branch. |
| `branch_no` | STRING | Branch number. |
| `tax_branch_code` | STRING | Branch code used for tax records. |
| `address_line1` | STRING | First address line for the branch. |
| `address_line2` | STRING | Second address line for the branch. |
| `sub_district` | STRING | Sub-district of the branch. |
| `district` | STRING | District of the branch. |
| `province` | STRING | Province of the branch. |
| `postal_code` | STRING | Postal code of the branch. |
| `country` | STRING | Country of the branch. |
| `geography_id` | STRING | Identifier of the geography associated with the branch. |
| `geography_code` | STRING | Code of the geography associated with the branch. |
| `geography_name` | STRING | Name of the geography associated with the branch. |
| `region_id` | STRING | Identifier of the region associated with the branch. |
| `region_code` | STRING | Code of the region associated with the branch. |
| `region_name` | STRING | Name of the region associated with the branch. |
| `latitude` | FLOAT64 | Latitude of the branch location in decimal degrees. |
| `longitude` | FLOAT64 | Longitude of the branch location in decimal degrees. |
| `google_map_url` | STRING | Map URL for the branch location. |
| `phone` | STRING | Branch telephone number. |
| `phone_ext` | STRING | Telephone extension for the branch. |
| `mobile` | STRING | Branch mobile telephone number. |
| `fax` | STRING | Branch fax number. |
| `email` | STRING | Branch email address. |
| `line_id` | STRING | LINE account identifier for the branch. |
| `website` | STRING | Branch website address. |
| `contact_person` | STRING | Name of the branch contact person. |
| `contact_position` | STRING | Position of the branch contact person. |
| `contact_phone` | STRING | Telephone number of the branch contact person. |
| `contact_email` | STRING | Email address of the branch contact person. |
| `delivery_address` | STRING | Delivery address for the branch. |
| `delivery_remark` | STRING | Delivery instructions for the branch. |
| `delivery_day` | STRING | Preferred delivery day for the branch. |
| `delivery_time` | STRING | Preferred delivery time for the branch. |
| `is_default` | BOOL | Whether this is the default branch for the customer. |
| `is_billing_address` | BOOL | Whether this branch is used as a billing address. |
| `is_shipping_address` | BOOL | Whether this branch is used as a shipping address. |
| `sort_order` | INT64 | Display order of the branch. |
| `remark` | STRING | Additional source remark about the branch. |
| `status` | STRING | Status of the source record. |
| `is_active` | STRING | Source active-state value for the branch. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Whether the record has been synchronized with the ERP. |
| `ASATDATE` | STRING | Hive partition containing the extract date from the GCS folder. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` with `CREATE OR REPLACE EXTERNAL TABLE`, preceded by `DROP TABLE IF EXISTS`.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_customer_branch/*`.
- The extract job writes files to GCS; the external table reads them directly.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_customer_branch`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', CURRENT_DATE('Asia/Bangkok'))
LIMIT 100
```

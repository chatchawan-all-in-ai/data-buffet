---
type: BigQuery Table
title: "crm_customer_branch"
description: "One row = one customer branch from source table `crm_customer_branch`, unique on (customer_branch_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_branch&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_branch
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_branch.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_customer_branch.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex/gpt-6", at: "2026-11-09T14:18:32+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_customer_branch`: source columns are cleaned or cast with shared helpers, the extract date is standardized to `asatdate`, and duplicate keys are collapsed. There is no business logic at this layer. Table meaning: Customer branch details, including contact, address and delivery information.

# Grain and key

One row per `customer_branch_id`. The key is declared in `uniqueKey` and `pk_key`, and added as a `NOT ENFORCED` primary key after full builds.

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
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Whether the record has been synchronized with the ERP. |
| `asatdate` | DATE | Extract date of the winning row, parsed from the raw ASATDATE partition; it is the deduplication tiebreaker and table partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_branch.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_branch](/initial/raw_derp/crm_customer_branch.md).
- Incremental runs read the configured ASATDATE lookback and merge on the source key; the first or full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY customer_branch_id ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_branch_id`.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_branch`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

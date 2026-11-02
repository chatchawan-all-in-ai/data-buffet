---
type: BigQuery Table
title: "sales_channel_master_sales_channel"
description: "One row = one sales channel node from source table `sales_channel_master_sales_channel`, unique on (master_sales_channel_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=sales_channel_master_sales_channel&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: sales_channel_master_sales_channel
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/sales_channel_master_sales_channel.sqlx"
    title: "Dataform definition (validated/derp/sales_channel_master_sales_channel.sqlx)"
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

Validated copy of DERP `sales_channel_master_sales_channel`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Hierarchy of sales channels with their document prefixes and quotation/sales-order approval and PO rules.
No other table or view in this repository reads it.

# Grain and key

One row per `master_sales_channel_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `master_sales_channel_id` | STRING | UUID of the sales channel. |
| `sales_channel_code` | STRING | Sales channel code (e.g. `MDT`, `EXPORT`, `ONL`, `RGB`). |
| `sales_channel_name` | STRING | Sales channel name. |
| `description` | STRING | Description of the sales channel. |
| `order_sort` | INT64 | Display order of the channel. |
| `level` | INT64 | Depth of the node in the hierarchy (1 = top level). |
| `parent_id` | STRING | UUID of the parent node in the same hierarchy (NULL at the top level). |
| `path_id` | STRING | Chain of channel UUIDs from the top level down to this channel, separated by `/`. |
| `path_code` | STRING | Chain of channel codes from the top level down to this channel, separated by `/` (e.g. `MDT/RGB`). |
| `path_name` | STRING | Chain of channel names from the top level down to this channel. |
| `company_code` | STRING | Code of the company that owns the record. |
| `organization_code` | STRING | Code of the organization that owns the record. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `prefix` | STRING | Document number prefix used for the channel (e.g. `RE`, `CRC`). |
| `billing_statement_prefix` | STRING | Document number prefix for billing statements of the channel. |
| `channel_group` | STRING | Channel group (`MDT`, `AGENT`, `RE`, `CRC`, `OTHER`). |
| `qt_mgr_approval` | BOOL | Flag showing quotations in the channel need sales-manager approval. |
| `qt_bu_approval` | BOOL | Flag showing quotations in the channel need business-unit approval. |
| `so_approver_type` | STRING | Approver type for sales orders in the channel (`SALE_MANAGER` or `CREDIT`). |
| `po_rule` | STRING | Customer purchase-order rule for the channel (`REQUIRED`, `NOT_REQUIRED`, `AGENT_CREDIT_PO_OR_MEMO`). |
| `default_order_delivery_type` | STRING | Default delivery type for orders in the channel. |
| `whole_bill_enforce` | BOOL | Flag forcing an order in the channel to be billed as a whole (no partial billing). |
| `project_required` | BOOL | Flag showing a project is required on documents in the channel. |
| `vendor_code_group_type` | STRING | Vendor code group type of the channel (e.g. `MDT`, `RE`, `CRC`). |
| `print_mac5_code` | BOOL | Flag showing the MAC5 customer code is printed on documents. |
| `require_export_declaration` | BOOL | Flag showing an export declaration is required in the channel. |
| `allow_so_without_qt` | BOOL | Flag allowing sales orders without a quotation in the channel. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/sales_channel_master_sales_channel.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.sales_channel_master_sales_channel](/initial/raw_derp/sales_channel_master_sales_channel.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `master_sales_channel_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 44 rows, 17.4 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.sales_channel_master_sales_channel`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT master_sales_channel_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.sales_channel_master_sales_channel`
GROUP BY master_sales_channel_id
HAVING n > 1
```

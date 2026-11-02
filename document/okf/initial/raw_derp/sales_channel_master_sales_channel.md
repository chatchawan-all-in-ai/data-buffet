---
type: BigQuery Table
title: "sales_channel_master_sales_channel"
description: "One row = one sales channel node, a record of source table `sales_channel_master_sales_channel` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=sales_channel_master_sales_channel&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: sales_channel_master_sales_channel
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

External table over AVRO files in `gs://file-raw-data/derp_temp/sales_channel_master_sales_channel/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `sales_channel_master_sales_channel` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Hierarchy of sales channels with their document prefixes and quotation/sales-order approval and PO rules. Used by: [validated_derp.sales_channel_master_sales_channel](/validated/validated_derp/sales_channel_master_sales_channel.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

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
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
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
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/sales_channel_master_sales_channel/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.sales_channel_master_sales_channel`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.sales_channel_master_sales_channel`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

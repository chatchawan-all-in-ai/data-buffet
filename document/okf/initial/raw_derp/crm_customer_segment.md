---
type: BigQuery Table
title: "crm_customer_segment"
description: "One row = one customer segment record, a record of source table `crm_customer_segment` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_customer_segment&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_customer_segment
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_customer_segment/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_customer_segment` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Segmentation attributes of each customer: customer group, customer type, company chain and category hierarchies.

Read by: [validated_derp.crm_customer_segment](/validated/validated_derp/crm_customer_segment.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_segment_id` | STRING | UUID of the customer segment record. |
| `customer_master_id` | STRING | UUID of the customer in `crm_customer_master`. |
| `customer_code` | STRING | Customer code in the CRM (e.g. `C0000136`; `NCT...` for new customers). |
| `customer_group_id` | STRING | Customer group code (e.g. `DOM` = domestic). |
| `item_customer_group` | STRING | Item customer group code used for pricing. |
| `customer_type` | STRING | Customer type (e.g. general company, real estate, modern trade, government). |
| `business_type` | STRING | Business type of the customer. |
| `company_chain` | STRING | Company chain (group) the customer belongs to. |
| `region` | STRING | Sales region of the customer. |
| `customer_category_level` | INT64 | Depth of the customer category in its hierarchy. |
| `customer_category_path` | STRING | Hierarchy path of the customer category. |
| `marketing_group_level` | INT64 | Depth of the marketing group in its hierarchy. |
| `marketing_group_path` | STRING | Hierarchy path of the marketing group. |
| `sales_group_level` | INT64 | Depth of the sales group in its hierarchy. |
| `sales_group_path` | STRING | Hierarchy path of the sales group. |
| `accounting_group_level` | INT64 | Depth of the accounting group in its hierarchy. |
| `accounting_group_path` | STRING | Hierarchy path of the accounting group. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Flag set when the record has been synchronized with the ERP (true for migrated customers, false for records created only in the CRM). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_customer_segment/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_customer_segment`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_customer_segment`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "crm_customer_segment"
description: "One row = one customer segment record from source table `crm_customer_segment`, unique on (customer_segment_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_segment&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_segment
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_segment.sqlx"
    title: "Dataform definition (validated/derp/crm_customer_segment.sqlx)"
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

Validated copy of DERP `crm_customer_segment`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Segmentation attributes of each customer: customer group, customer type, company chain and category hierarchies.
No other repo object reads it.

# Grain and key

One row per `customer_segment_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Flag set when the record has been synchronized with the ERP (true for migrated customers, false for records created only in the CRM). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_segment.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_segment](/initial/raw_derp/crm_customer_segment.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_segment_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_segment`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT customer_segment_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_customer_segment`
GROUP BY customer_segment_id
HAVING n > 1
```

---
type: BigQuery Table
title: "crm_customer_master"
description: "One row = one cleaned copy of the source table `crm_customer_master`, unique on (customer_master_id)."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_customer_master`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `customer_master_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_master_id` | STRING | Meaning not documented in the repo. |
| `customer_code` | STRING | Meaning not documented in the repo. |
| `mac5_code` | STRING | Meaning not documented in the repo. |
| `d365_party_id` | STRING | Meaning not documented in the repo. |
| `party_type` | STRING | Meaning not documented in the repo. |
| `party_type_raw` | STRING | Meaning not documented in the repo. |
| `tax_id` | STRING | Meaning not documented in the repo. |
| `organization_name_th` | STRING | Meaning not documented in the repo. |
| `organization_name_en` | STRING | Meaning not documented in the repo. |
| `short_name_th` | STRING | Meaning not documented in the repo. |
| `short_name_en` | STRING | Meaning not documented in the repo. |
| `acronym_th` | STRING | Meaning not documented in the repo. |
| `acronym_en` | STRING | Meaning not documented in the repo. |
| `search_name` | STRING | Meaning not documented in the repo. |
| `prefix_name` | STRING | Meaning not documented in the repo. |
| `first_name_th` | STRING | Meaning not documented in the repo. |
| `last_name_th` | STRING | Meaning not documented in the repo. |
| `middle_name_th` | STRING | Meaning not documented in the repo. |
| `first_name_en` | STRING | Meaning not documented in the repo. |
| `last_name_en` | STRING | Meaning not documented in the repo. |
| `middle_name_en` | STRING | Meaning not documented in the repo. |
| `branch_code` | STRING | Meaning not documented in the repo. |
| `branch_name` | STRING | Meaning not documented in the repo. |
| `is_one_time` | BOOL | Meaning not documented in the repo. |
| `invoice_account` | STRING | Meaning not documented in the repo. |
| `order_account` | STRING | Meaning not documented in the repo. |
| `delivery_account` | STRING | Meaning not documented in the repo. |
| `withholding_tax_code` | STRING | Meaning not documented in the repo. |
| `withholding_tax_rate` | FLOAT64 | Meaning not documented in the repo. |
| `vat_code` | STRING | Meaning not documented in the repo. |
| `vat_rate` | FLOAT64 | Meaning not documented in the repo. |
| `sales_tax_group` | STRING | Meaning not documented in the repo. |
| `currency` | STRING | Meaning not documented in the repo. |
| `language` | STRING | Meaning not documented in the repo. |
| `website` | STRING | Meaning not documented in the repo. |
| `grade` | STRING | Meaning not documented in the repo. |
| `book3_color` | STRING | Meaning not documented in the repo. |
| `store_code` | STRING | Meaning not documented in the repo. |
| `store_name` | STRING | Meaning not documented in the repo. |
| `sales_remark` | STRING | Meaning not documented in the repo. |
| `account_remark` | STRING | Meaning not documented in the repo. |
| `marketing_remark` | STRING | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `full_text_search` | STRING | Meaning not documented in the repo. |
| `is_new_customer` | BOOL | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `updated_by_name` | STRING | Meaning not documented in the repo. |
| `is_sync` | BOOL | Meaning not documented in the repo. |
| `require_po` | BOOL | Meaning not documented in the repo. |
| `customer_known_as` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_master.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_master](/initial/raw_derp/crm_customer_master.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_master_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 22,547 rows, 24.6 MB.

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

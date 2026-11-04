---
type: BigQuery Table
title: "crm_customer_credit"
description: "One row = one customer credit record from source table `crm_customer_credit`, unique on (customer_credit_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_credit&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_credit
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_credit.sqlx"
    title: "Dataform definition (validated/derp/crm_customer_credit.sqlx)"
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

Validated copy of DERP `crm_customer_credit`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Credit settings of CRM customers: credit limit, credit and payment terms, credit status and collateral.
No other table or view in this repository reads it.

# Grain and key

One row per `customer_credit_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_credit_id` | STRING | UUID of the customer credit record. |
| `customer_master_id` | STRING | UUID of the customer in `crm_customer_master`. |
| `customer_code` | STRING | Customer code in the CRM (e.g. `C0000136`; `NCT...` for new customers). |
| `credit_limit` | FLOAT64 | Credit limit of the customer in THB (0 = no credit). |
| `credit_limit_change_date` | DATE | Date the credit limit was last changed. |
| `credit_term` | STRING | Credit term code (e.g. `N000` = cash, `N030` = 30 days). |
| `credit_rating` | STRING | Credit rating of the customer. |
| `credit_scoring` | FLOAT64 | Credit score of the customer. |
| `credit_status` | STRING | Credit status (e.g. `NORMAL`). |
| `credit_management_group` | STRING | Credit management group (customer chain) the customer is managed under. |
| `payment_term` | STRING | Payment term code (e.g. `N000`, `N030`). |
| `payment_method` | STRING | Payment method of the customer. |
| `payment_condition` | STRING | Payment condition of the customer. |
| `collateral_type` | STRING | Type of collateral held for the credit. |
| `collateral_start_date` | DATE | Start date of the collateral. |
| `collateral_end_date` | DATE | End date of the collateral. |
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

- Definition: `definitions/validated/derp/crm_customer_credit.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_credit](/initial/raw_derp/crm_customer_credit.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_credit_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_credit`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT customer_credit_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_customer_credit`
GROUP BY customer_credit_id
HAVING n > 1
```

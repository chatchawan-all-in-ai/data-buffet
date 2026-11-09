---
type: BigQuery Table
title: "crm_customer_bank_account"
description: "One row = one customer bank account from source table `crm_customer_bank_account`, unique on (customer_bank_account_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_bank_account&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_bank_account
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_bank_account.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_customer_bank_account.sqlx)"
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

Validated copy of DERP `crm_customer_bank_account`: source columns are cleaned or cast with shared helpers, the extract date is standardized to `asatdate`, and duplicate keys are collapsed. There is no business logic at this layer. Table meaning: Customer bank accounts registered in CRM.

# Grain and key

One row per `customer_bank_account_id`. The key is declared in `uniqueKey` and `pk_key`, and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_bank_account_id` | STRING | Source identifier of the customer bank-account record. |
| `customer_master_id` | STRING | Identifier of the customer record. |
| `customer_code` | STRING | Customer code from CRM. |
| `bank_name` | STRING | Name of the bank holding the account. |
| `bank_account_number` | STRING | Bank account number. |
| `bank_account_name` | STRING | Name registered on the bank account. |
| `is_primary` | BOOL | Whether this is the primary bank account for the customer. |
| `status` | STRING | Status of the source record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Whether the record has been synchronized with the ERP. |
| `asatdate` | DATE | Extract date of the winning row, parsed from the raw ASATDATE partition; it is the deduplication tiebreaker and table partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_bank_account.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_bank_account](/initial/raw_derp/crm_customer_bank_account.md).
- Incremental runs read the configured ASATDATE lookback and merge on the source key; the first or full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY customer_bank_account_id ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_bank_account_id`.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_bank_account`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

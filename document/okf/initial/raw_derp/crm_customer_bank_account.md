---
type: BigQuery Table
title: "crm_customer_bank_account"
description: "One row = one customer bank account, a record of source table `crm_customer_bank_account` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_customer_bank_account&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_customer_bank_account
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_customer_bank_account/*` (Hive-partitioned by `ASATDATE`). It is the raw landing copy of the `crm_customer_bank_account` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Customer bank accounts registered in CRM.

Read by: [validated_derp.crm_customer_bank_account](/validated/validated_derp/crm_customer_bank_account.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; see the [validated table card](/validated/validated_derp/crm_customer_bank_account.md#how-it-is-built) for its key and deduplication rules.

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
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_customer_bank_account/*`.
- The extract job writes files to GCS; the external table reads them directly.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_customer_bank_account`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', CURRENT_DATE('Asia/Bangkok'))
LIMIT 100
```

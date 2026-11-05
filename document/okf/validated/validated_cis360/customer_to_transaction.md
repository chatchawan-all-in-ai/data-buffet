---
type: BigQuery Table
title: "customer_to_transaction"
description: "One row = one buyer-seller transaction from source table `customer_to_transaction`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_cis360&t=customer_to_transaction&page=table"
project_id: databuffet-nonprd
dataset_id: validated_cis360
table_id: customer_to_transaction
tags: ["validated", "validated_cis360", "cis360", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/cis360/customer_to_transaction.sqlx"
    title: "Dataform definition (validated/cis360/customer_to_transaction.sqlx)"
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

Validated copy of CIS360 `customer_to_transaction`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Purchase transactions between CIS360 buyer and seller profiles recorded from the Allkons M platform, with item count and total amount.
No other table or view in this repository reads it.

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the transaction record. |
| `buyer_id` | STRING | Customer profile of the buyer (`customer_profile.id`). |
| `seller_id` | STRING | Customer profile of the seller (`customer_profile.id`). |
| `transaction_type_id` | INT64 | Transaction type code (values 1, 2; type 2 carries a `platform_reference_id`). |
| `platform_id` | INT64 | Platform where the transaction was made (1 = ALLKONS_M_BUYER). |
| `platform_reference_id` | INT64 | Reference identifier of the transaction on the source platform. |
| `buyer_name` | STRING | Name of the buyer. |
| `seller_name` | STRING | Name of the seller. |
| `transaction_code` | STRING | Document code of the transaction on Allkons M (e.g. `QOAG-` + digits). |
| `total_items` | INT64 | Number of items in the transaction. |
| `total_amount` | FLOAT64 | Total amount of the transaction in THB. |
| `url_reference` | STRING | URL reference of the transaction (not populated in current data). |
| `is_delete` | BOOL | Soft-delete flag (TRUE = record deleted). |
| `transaction_date` | DATETIME | Date and time of the transaction. |
| `create_date` | DATETIME | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | DATETIME | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/cis360/customer_to_transaction.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_cis360.customer_to_transaction](/initial/raw_cis360/customer_to_transaction.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_cis360.customer_to_transaction`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_cis360.customer_to_transaction`
GROUP BY id
HAVING n > 1
```

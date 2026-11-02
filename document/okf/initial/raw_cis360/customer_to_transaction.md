---
type: BigQuery Table
title: "customer_to_transaction"
description: "One row = one buyer-seller transaction, a record of source table `customer_to_transaction` (CIS360) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_cis360&t=customer_to_transaction&page=table"
project_id: databuffet-nonprd
dataset_id: raw_cis360
table_id: customer_to_transaction
tags: ["initial", "raw_cis360", "cis360"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/cis360/create_all_table_raw_cis360.sqlx"
    title: "Dataform definition (initial/cis360/create_all_table_raw_cis360.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/cis360/customer_to_transaction/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `customer_to_transaction` table from CIS360; nothing is cleaned or deduplicated here. Table meaning: Purchase transactions between CIS360 buyer and seller profiles recorded from the Allkons M platform, with item count and total amount. Used by: [validated_cis360.customer_to_transaction](/validated/validated_cis360/customer_to_transaction.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

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
| `transaction_date` | STRING | Date and time of the transaction. |
| `create_date` | STRING | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | STRING | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_cis360` (`definitions/initial/cis360/create_all_table_raw_cis360.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/cis360/customer_to_transaction/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_cis360.customer_to_transaction`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_cis360.customer_to_transaction`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "marketing_condition_version_details"
description: "One row = one version of a commission condition, a record of source table `marketing_condition_version_details` (ALLKONS_COMMISSION) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_allkons_commission&t=marketing_condition_version_details&page=table"
project_id: databuffet-nonprd
dataset_id: raw_allkons_commission
table_id: marketing_condition_version_details
tags: ["initial", "raw_allkons_commission", "allkons"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx"
    title: "Dataform definition (initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/allkons_commission/marketing_condition_version_details/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `marketing_condition_version_details` table from ALLKONS_COMMISSION; nothing is cleaned or deduplicated here. Table meaning: Versioned commission and incentive conditions: calculation method, eligible positions, channels and territories, date ranges and rule definition.

No other repo object reads it.

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `code` | STRING | Commission condition code (e.g. `MC548`). |
| `id` | STRING | Unique identifier (UUID) of the condition version. |
| `marketing_condition_id` | STRING | Commission condition this version belongs to. |
| `version_no` | INT64 | Version number of the condition (0 = first version). |
| `condition_type` | STRING | Commission calculation method (`PER_ITEM`, `TIER_DISCOUNT`, `MARGIN`, `TARGET_ACHIEVEMENT`). |
| `name` | STRING | Name of the commission condition. |
| `type` | STRING | Kind of payout (`COMMISSION`, `INCENTIVE`). |
| `status` | STRING | Condition status (`ACTIVE`, `INACTIVE`). |
| `sales_positions` | STRING | JSON array of sales positions the condition applies to (e.g. TA, PC). |
| `sales_channels` | STRING | JSON array of sales channels the condition applies to. |
| `territories` | STRING | JSON array of territories the condition applies to (type `COUNTRY`, `REGION` or `PROVINCE`). |
| `commission_payment_type` | STRING | When commission becomes payable (`PAYMENT_SUCCESSFUL` = after customer payment, `NONE`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `content_changed_at` | STRING | Timestamp when the condition content last changed. |
| `accounting_period_type` | STRING | Accounting period unit (`DAILY`, `MONTHLY`, `QUARTERLY`, `YEARLY`). |
| `accounting_period_value` | STRING | Number of accounting period units. |
| `invoice_start_date` | STRING | Start of the invoice date range covered by the condition (UTC). |
| `invoice_end_date` | STRING | End of the invoice date range covered by the condition (UTC). |
| `order_start_date` | STRING | Start of the order date range covered by the condition (UTC). |
| `order_end_date` | STRING | End of the order date range covered by the condition (UTC). |
| `additional_commission_conditions` | STRING | JSON array of extra calculation rules (e.g. `FROM_FIRST_AMOUNT`, `SPLIT_AMOUNT_BETWEEN_PC_AND_TA`, `IF_NO_PC_THEN_TA_SELL_DIRECTLY`). |
| `data` | STRING | JSON definition of the condition rules (products, product groups, margin ranges, rates). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_allkons_commission` (`definitions/initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/allkons_commission/marketing_condition_version_details/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_allkons_commission.marketing_condition_version_details`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_allkons_commission.marketing_condition_version_details`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

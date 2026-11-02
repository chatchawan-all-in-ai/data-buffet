---
type: BigQuery Table
title: "crm_sale_order_payment"
description: "One row = one payment plan of a sale order, a record of source table `crm_sale_order_payment` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_sale_order_payment&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_sale_order_payment
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order_payment/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order_payment` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Payment plans of DERP sale orders: payment method, term, condition and amount. Used by: [validated_derp.crm_sale_order_payment](/validated/validated_derp/crm_sale_order_payment.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_payment_id` | STRING | Unique identifier of the sale order payment plan. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `payment_seq` | INT64 | Sequence number of the payment plan within the sale order. |
| `payment_method_id` | STRING | Identifier of the payment method. |
| `payment_method_code` | STRING | Payment method code (e.g. `BANK_TRANSFER`, `CASH`, `CHEQUE`, `CREDIT_LIMIT`, `BILL_PAYMENT`, `OTHER_FINANCE`). |
| `payment_method_name` | STRING | Payment method name in Thai. |
| `payment_term_id` | STRING | Identifier of the payment term. |
| `payment_term_code` | STRING | Payment term code (`N000`/`N030`/`N060` = pay 0/30/60 days after delivery, `N888` = no term). |
| `payment_term_name` | STRING | Payment term description in Thai (e.g. pay 60 days after delivery). |
| `payment_term_other` | STRING | Free-text payment term entered when no standard term applies. |
| `payment_condition_id` | STRING | Identifier of the payment condition. |
| `payment_condition_code` | STRING | Payment condition code (e.g. `BP_CRM` = by billing cycle, `BFF_LMS` = before delivery, `NOW_LMS` = on delivery, `AFT_LMS` = after delivery, `OTHER`). |
| `payment_condition_name` | STRING | Payment condition description in Thai. |
| `payment_condition_other` | STRING | Free-text payment condition entered when no standard condition applies. |
| `amount` | FLOAT64 | Amount covered by the payment plan (THB). |
| `percent` | FLOAT64 | Share of the order amount covered by the payment plan, in percent. |
| `detail` | STRING | Free-text description of the payment plan. |
| `order_sort` | INT64 | Display order of the row within its sale order, starting at 0. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_sale_order_payment/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_sale_order_payment`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_sale_order_payment`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

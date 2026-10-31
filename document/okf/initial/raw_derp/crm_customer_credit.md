---
type: BigQuery Table
title: "crm_customer_credit"
description: "One row = one record of source table `crm_customer_credit` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_customer_credit&page=table"
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_customer_credit/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_customer_credit` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.crm_customer_credit](/validated/validated_derp/crm_customer_credit.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_credit_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_master_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `customer_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_limit` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_limit_change_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_term` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_rating` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_scoring` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `credit_management_group` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_term` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_method` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `payment_condition` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `collateral_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `collateral_start_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `collateral_end_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `status` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `is_sync` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_customer_credit/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_customer_credit`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_customer_credit`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

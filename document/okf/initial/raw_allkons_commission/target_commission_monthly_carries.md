---
type: BigQuery Table
title: "target_commission_monthly_carries"
description: "One row = one monthly target carry-over for a salesperson and condition version, a record of source table `target_commission_monthly_carries` (ALLKONS_COMMISSION) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_allkons_commission&t=target_commission_monthly_carries&page=table"
project_id: databuffet-nonprd
dataset_id: raw_allkons_commission
table_id: target_commission_monthly_carries
tags: ["initial", "raw_allkons_commission", "allkons"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx"
    title: "Dataform definition (initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/allkons_commission/target_commission_monthly_carries/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `target_commission_monthly_carries` table from ALLKONS_COMMISSION; nothing is cleaned or deduplicated here. Table meaning: Remaining sales-target amounts carried over month to month per salesperson and commission condition version.

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the carry-over record. |
| `marketing_condition_version_id` | STRING | Commission condition version the carry-over belongs to (`marketing_condition_version_details.id`). |
| `sales_id` | STRING | Employee code of the salesperson. |
| `month_key` | STRING | Month of the carry-over (`YYYY-MM`). |
| `sales_target_unit` | STRING | Unit of the sales target (`THB`). |
| `leftover` | FLOAT64 | Remaining target amount carried over to the next month, in the target unit. |
| `job_id` | STRING | Identifier of the calculation job that produced the record. |
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_allkons_commission` (`definitions/initial/allkons_commission/create_all_table_raw_allkons_commission.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/allkons_commission/target_commission_monthly_carries/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_allkons_commission.target_commission_monthly_carries`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_allkons_commission.target_commission_monthly_carries`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

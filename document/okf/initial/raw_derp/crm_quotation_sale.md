---
type: BigQuery Table
title: "crm_quotation_sale"
description: "One row = one salesperson on a quotation, a record of source table `crm_quotation_sale` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_quotation_sale&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_quotation_sale
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_quotation_sale/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_quotation_sale` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Salespeople credited on each quotation with their share of the sales amount and commission rate.

Read by: [validated_derp.crm_quotation_sale](/validated/validated_derp/crm_quotation_sale.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_sale_id` | STRING | UUID of the quotation salesperson record. |
| `quotation_id` | STRING | UUID of the quotation in `crm_quotation`. |
| `quotation_no` | STRING | Quotation document number (e.g. `QT2607...` or `MDT2610...`). |
| `quotation_date` | STRING | Quotation document date. |
| `sales_seq` | INT64 | Sequence number of the salesperson on the quotation (1 = first). |
| `sales_id` | STRING | UUID of the salesperson (employee) record. |
| `sales_code` | STRING | Employee number of the salesperson. |
| `sales_name` | STRING | Name of the salesperson. |
| `sales_amount` | FLOAT64 | Sales amount credited to the salesperson, in THB. |
| `sales_amount_pct` | FLOAT64 | Share of the quotation amount credited to the salesperson, in percent. |
| `commission_pct` | FLOAT64 | Commission rate of the salesperson, in percent. |
| `order_sort` | INT64 | Display order of the row within its parent record. |
| `path_id` | STRING | Chain of sales-territory UUIDs of the salesperson. |
| `path_code` | STRING | Chain of sales-territory codes of the salesperson. |
| `path_name` | STRING | Chain of sales-territory names of the salesperson. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_quotation_sale/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_quotation_sale`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_quotation_sale`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

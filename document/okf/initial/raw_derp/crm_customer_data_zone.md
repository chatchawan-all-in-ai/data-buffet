---
type: BigQuery Table
title: "crm_customer_data_zone"
description: "One row = one assignment of a customer to a data zone, a record of source table `crm_customer_data_zone` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_customer_data_zone&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_customer_data_zone
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_customer_data_zone/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_customer_data_zone` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Assignments of CRM customers to data zones (three-level zone hierarchy) for main or logistics purposes. Used by: [validated_derp.crm_customer_data_zone](/validated/validated_derp/crm_customer_data_zone.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_data_zone_id` | STRING | UUID of the customer data-zone assignment. |
| `customer_master_id` | STRING | UUID of the customer in `crm_customer_master`. |
| `customer_code` | STRING | Customer code in the CRM (e.g. `C0000136`; `NCT...` for new customers). |
| `data_zone_id` | STRING | UUID of the assigned (lowest-level) data zone in `crm_data_zone`. |
| `level1_id` | STRING | UUID of the level-1 data zone. |
| `level1_code` | STRING | Code of the level-1 data zone. |
| `level1_name` | STRING | Name of the level-1 data zone. |
| `level2_id` | STRING | UUID of the level-2 data zone. |
| `level2_code` | STRING | Code of the level-2 data zone. |
| `level2_name` | STRING | Name of the level-2 data zone. |
| `level3_id` | STRING | UUID of the level-3 data zone. |
| `level3_code` | STRING | Code of the level-3 data zone. |
| `level3_name` | STRING | Name of the level-3 data zone. |
| `path_id` | STRING | Chain of data-zone UUIDs from level 1 down to the assigned zone. |
| `path_code` | STRING | Chain of data-zone codes from level 1 down to the assigned zone. |
| `path_name` | STRING | Chain of data-zone names from level 1 down to the assigned zone. |
| `zone_type` | STRING | Purpose of the zone assignment (`MAIN` or `LOGISTICS`). |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `valid_from` | STRING | Date from which the assignment is valid. |
| `valid_to` | STRING | Date until which the assignment is valid (NULL = open-ended). |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_customer_data_zone/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_customer_data_zone`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_customer_data_zone`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

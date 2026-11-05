---
type: BigQuery Table
title: "crm_business_unit"
description: "One row = one business unit node, a record of source table `crm_business_unit` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_business_unit&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_business_unit
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_business_unit/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_business_unit` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Business unit (product line) hierarchy of the CRM, with the responsible employee and two alternates per unit.

Read by: [validated_derp.crm_business_unit](/validated/validated_derp/crm_business_unit.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `business_unit_id` | STRING | UUID of the business unit. |
| `bu_code` | STRING | Business unit code (e.g. `0311`; hierarchical, child codes extend the parent code). |
| `bu_name` | STRING | Business unit name. |
| `bu_description` | STRING | Description of the business unit (product line). |
| `level` | INT64 | Depth of the node in the hierarchy (1 = top level). |
| `parent_id` | STRING | UUID of the parent node in the same hierarchy (NULL at the top level). |
| `parent_code` | STRING | Code of the parent business unit. |
| `path_id` | STRING | Chain of business-unit UUIDs from the top level down to this unit. |
| `path_code` | STRING | Chain of business-unit codes from the top level down to this unit (e.g. `03`, `031`, `0311`). |
| `path_name` | STRING | Chain of business-unit names from the top level down to this unit. |
| `company_id` | STRING | UUID of the company that owns the record. |
| `company_code` | STRING | Code of the company that owns the record. |
| `organization_id` | STRING | UUID of the organization that owns the record. |
| `organization_code` | STRING | Code of the organization that owns the record. |
| `responsible_employee_id` | STRING | UUID of the employee responsible for the business unit. |
| `responsible_employee_no` | STRING | Employee number of the employee responsible for the business unit. |
| `responsible_user_id` | STRING | User UUID of the employee responsible for the business unit. |
| `responsible_name` | STRING | Name of the employee responsible for the business unit. |
| `responsible_effective_date` | STRING | Date the responsible employee assignment starts. |
| `responsible_expiry_date` | STRING | Date the responsible employee assignment ends. |
| `alt1_employee_id` | STRING | UUID of the first alternate responsible employee. |
| `alt1_employee_no` | STRING | Employee number of the first alternate responsible employee. |
| `alt1_user_id` | STRING | User UUID of the first alternate responsible employee. |
| `alt1_name` | STRING | Name of the first alternate responsible employee. |
| `alt1_effective_date` | STRING | Date the first alternate assignment starts. |
| `alt1_expiry_date` | STRING | Date the first alternate assignment ends. |
| `alt2_employee_id` | STRING | UUID of the second alternate responsible employee. |
| `alt2_employee_no` | STRING | Employee number of the second alternate responsible employee. |
| `alt2_user_id` | STRING | User UUID of the second alternate responsible employee. |
| `alt2_name` | STRING | Name of the second alternate responsible employee. |
| `alt2_effective_date` | STRING | Date the second alternate assignment starts. |
| `alt2_expiry_date` | STRING | Date the second alternate assignment ends. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_business_unit/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_business_unit`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_business_unit`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

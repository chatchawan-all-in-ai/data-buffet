---
type: BigQuery Table
title: "crm_quotation_terr_cust"
description: "One row = one customer assignment for a quotation territory, a record of source table `crm_quotation_terr_cust` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_quotation_terr_cust&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_quotation_terr_cust
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_quotation_terr_cust/*` (Hive-partitioned by `ASATDATE`). It is the raw landing copy of the `crm_quotation_terr_cust` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Customer and organization assignments recorded for a quotation territory.

Read by: [validated_derp.crm_quotation_terr_cust](/validated/validated_derp/crm_quotation_terr_cust.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; see the [validated table card](/validated/validated_derp/crm_quotation_terr_cust.md#how-it-is-built) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_terr_cust_id` | STRING | Source identifier of the quotation-territory customer record. |
| `quotation_id` | STRING | Identifier of the quotation. |
| `quotation_date` | STRING | Date of the quotation. |
| `quotation_no` | STRING | Quotation number. |
| `customer_id` | STRING | Identifier of the customer assigned to the quotation territory. |
| `customer_code` | STRING | Customer code from CRM. |
| `customer_name` | STRING | Name of the customer assigned to the quotation territory. |
| `department_id` | STRING | Identifier of the department in the assignment hierarchy. |
| `department_code` | STRING | Code of the department in the assignment hierarchy. |
| `department_name` | STRING | Name of the department in the assignment hierarchy. |
| `section_id` | STRING | Identifier of the section in the assignment hierarchy. |
| `section_code` | STRING | Code of the section in the assignment hierarchy. |
| `section_name` | STRING | Name of the section in the assignment hierarchy. |
| `division_id` | STRING | Identifier of the division in the assignment hierarchy. |
| `division_code` | STRING | Code of the division in the assignment hierarchy. |
| `division_name` | STRING | Name of the division in the assignment hierarchy. |
| `ta_area_id` | STRING | Identifier of the TA area in the assignment hierarchy. |
| `ta_area_code` | STRING | Code of the TA area in the assignment hierarchy. |
| `ta_area_name` | STRING | Name of the TA area in the assignment hierarchy. |
| `path_id` | STRING | Identifier of the sales path in the assignment hierarchy. |
| `path_code` | STRING | Code of the sales path in the assignment hierarchy. |
| `path_name` | STRING | Name of the sales path in the assignment hierarchy. |
| `status` | STRING | Status of the source record. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition containing the extract date from the GCS folder. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` with `CREATE OR REPLACE EXTERNAL TABLE`, preceded by `DROP TABLE IF EXISTS`.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_quotation_terr_cust/*`.
- The extract job writes files to GCS; the external table reads them directly.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_quotation_terr_cust`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', CURRENT_DATE('Asia/Bangkok'))
LIMIT 100
```

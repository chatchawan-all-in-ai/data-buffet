---
type: BigQuery Table
title: "sales_sales_territory"
description: "One row = one sales territory node, a record of source table `sales_sales_territory` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=sales_sales_territory&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: sales_sales_territory
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

External table over AVRO files in `gs://file-raw-data/derp_temp/sales_sales_territory/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `sales_sales_territory` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Hierarchy of sales territories (up to four levels) with code, name and validity dates. Used by: [validated_derp.sales_sales_territory](/validated/validated_derp/sales_sales_territory.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_territory_id` | STRING | UUID of the sales territory. |
| `code` | STRING | Sales territory code (e.g. `SV13_0_TA_01`). |
| `name` | STRING | Sales territory name. |
| `description` | STRING | Description of the sales territory. |
| `level` | INT64 | Depth of the node in the hierarchy (1 = top level). |
| `parent_id` | STRING | UUID of the parent node in the same hierarchy (NULL at the top level). |
| `path_id` | STRING | Chain of territory UUIDs from the top level down to this territory, separated by `/`. |
| `path_code` | STRING | Chain of territory codes from the top level down to this territory, separated by `/` (e.g. `SV/SV_13/SV13_0/SV13_0_TA_01/`). |
| `path_name` | STRING | Chain of territory names from the top level down to this territory, separated by `/`. |
| `valid_from` | STRING | Date from which the territory is valid. |
| `valid_to` | STRING | Date until which the territory is valid (NULL = open-ended). |
| `company_id` | STRING | UUID of the company that owns the record. |
| `company_code` | STRING | Code of the company that owns the record. |
| `organization_id` | STRING | UUID of the organization that owns the record. |
| `organization_code` | STRING | Code of the organization that owns the record. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/sales_sales_territory/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.sales_sales_territory`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.sales_sales_territory`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

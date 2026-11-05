---
type: BigQuery Table
title: "product_group_cost_group"
description: "One row = one product group cost-group assignment, a record of source table `product_group_cost_group` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=product_group_cost_group&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mastersku
table_id: product_group_cost_group
tags: ["initial", "raw_mastersku", "mastersku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx"
    title: "Dataform definition (initial/mastersku/create_all_table_raw_mastersku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mastersku/product_group_cost_group/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `product_group_cost_group` table from MASTERSKU; nothing is cleaned or deduplicated here. Table meaning: Cost groups assigned to each MASTERSKU product group.

Read by: [validated_mastersku.product_group_cost_group](/validated/validated_mastersku/product_group_cost_group.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `pgcg_id` | STRING | Unique identifier (UUID) of the cost-group assignment. |
| `pgcg_pg_id` | STRING | Product group (FK to `product_group.pg_id`). |
| `pgcg_cost_group_detail` | STRING | Cost groups assigned to the product group as a JSON array of identifiers. |
| `pgcg_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `pgcg_create_date` | STRING | Timestamp when the record was created. |
| `pgcg_create_by` | STRING | Identifier of the user who created the record. |
| `pgcg_update_date` | STRING | Timestamp when the record was last updated. |
| `pgcg_update_by` | STRING | Identifier of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mastersku` (`definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mastersku/product_group_cost_group/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mastersku.product_group_cost_group`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mastersku.product_group_cost_group`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

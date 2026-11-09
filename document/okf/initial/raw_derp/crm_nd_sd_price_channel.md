---
type: BigQuery Table
title: "crm_nd_sd_price_channel"
description: "One row = one sales-channel association for an ND/SD price, a record of source table `crm_nd_sd_price_channel` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_nd_sd_price_channel&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_nd_sd_price_channel
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_nd_sd_price_channel/*` (Hive-partitioned by `ASATDATE`). It is the raw landing copy of the `crm_nd_sd_price_channel` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Sales-channel associations for ND/SD prices.

Read by: [validated_derp.crm_nd_sd_price_channel](/validated/validated_derp/crm_nd_sd_price_channel.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; see the [validated table card](/validated/validated_derp/crm_nd_sd_price_channel.md#how-it-is-built) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `nd_sd_price_channel_id` | STRING | Source identifier of the ND/SD price-channel record. |
| `nd_sd_price_id` | STRING | Identifier of the associated ND/SD price. |
| `master_sales_channel_id` | STRING | Identifier of the associated master sales channel. |
| `sales_channel_code` | STRING | Code of the associated sales channel. |
| `sales_channel_name` | STRING | Name of the associated sales channel. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition containing the extract date from the GCS folder. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` with `CREATE OR REPLACE EXTERNAL TABLE`, preceded by `DROP TABLE IF EXISTS`.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_nd_sd_price_channel/*`.
- The extract job writes files to GCS; the external table reads them directly.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_nd_sd_price_channel`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', CURRENT_DATE('Asia/Bangkok'))
LIMIT 100
```

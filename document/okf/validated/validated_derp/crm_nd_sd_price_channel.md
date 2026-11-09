---
type: BigQuery Table
title: "crm_nd_sd_price_channel"
description: "One row = one sales-channel association for an ND/SD price from source table `crm_nd_sd_price_channel`, unique on (nd_sd_price_channel_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_nd_sd_price_channel&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_nd_sd_price_channel
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_nd_sd_price_channel.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_nd_sd_price_channel.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex/gpt-6", at: "2026-11-09T14:18:32+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_nd_sd_price_channel`: source columns are cleaned or cast with shared helpers, the extract date is standardized to `asatdate`, and duplicate keys are collapsed. There is no business logic at this layer. Table meaning: Sales-channel associations for ND/SD prices.

# Grain and key

One row per `nd_sd_price_channel_id`. The key is declared in `uniqueKey` and `pk_key`, and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `nd_sd_price_channel_id` | STRING | Source identifier of the ND/SD price-channel record. |
| `nd_sd_price_id` | STRING | Identifier of the associated ND/SD price. |
| `master_sales_channel_id` | STRING | Identifier of the associated master sales channel. |
| `sales_channel_code` | STRING | Code of the associated sales channel. |
| `sales_channel_name` | STRING | Name of the associated sales channel. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date of the winning row, parsed from the raw ASATDATE partition; it is the deduplication tiebreaker and table partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_nd_sd_price_channel.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_nd_sd_price_channel](/initial/raw_derp/crm_nd_sd_price_channel.md).
- Incremental runs read the configured ASATDATE lookback and merge on the source key; the first or full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY nd_sd_price_channel_id ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `nd_sd_price_channel_id`.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_nd_sd_price_channel`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

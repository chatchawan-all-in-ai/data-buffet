---
type: BigQuery Table
title: "crm_nd_sd_price_zone"
description: "One row = one link between an ND/SD price and a data zone from source table `crm_nd_sd_price_zone`, unique on (nd_sd_price_zone_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_nd_sd_price_zone&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_nd_sd_price_zone
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_nd_sd_price_zone.sqlx"
    title: "Dataform definition (validated/derp/crm_nd_sd_price_zone.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_nd_sd_price_zone`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Data zones each ND/SD price applies to.
No other table or view in this repository reads it.

# Grain and key

One row per `nd_sd_price_zone_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `nd_sd_price_zone_id` | STRING | UUID of the price-to-data-zone link. |
| `nd_sd_price_id` | STRING | UUID of the ND/SD price record in `crm_nd_sd_price`. |
| `data_zone_id` | STRING | UUID of the data zone in `crm_data_zone`. |
| `data_zone_code` | STRING | Code of the data zone the price applies to. |
| `data_zone_name` | STRING | Name of the data zone the price applies to. |
| `data_zone_level` | INT64 | Hierarchy level of the data zone (1 = top level). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_nd_sd_price_zone.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_nd_sd_price_zone](/initial/raw_derp/crm_nd_sd_price_zone.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `nd_sd_price_zone_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_nd_sd_price_zone`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT nd_sd_price_zone_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_nd_sd_price_zone`
GROUP BY nd_sd_price_zone_id
HAVING n > 1
```

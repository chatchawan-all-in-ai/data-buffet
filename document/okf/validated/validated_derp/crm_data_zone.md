---
type: BigQuery Table
title: "crm_data_zone"
description: "One row = one data zone node from source table `crm_data_zone`, unique on (data_zone_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_data_zone&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_data_zone
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_data_zone.sqlx"
    title: "Dataform definition (validated/derp/crm_data_zone.sqlx)"
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

Validated copy of DERP `crm_data_zone`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Hierarchy of data zones (up to three levels) used to group customers and prices.
No other table or view in this repository reads it.

# Grain and key

One row per `data_zone_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `data_zone_id` | STRING | UUID of the data zone. |
| `code` | STRING | Data zone code. |
| `name` | STRING | Data zone name. |
| `description` | STRING | Description of the data zone. |
| `level` | INT64 | Depth of the node in the hierarchy (1 = top level). |
| `parent_id` | STRING | UUID of the parent node in the same hierarchy (NULL at the top level). |
| `path_id` | STRING | Chain of data-zone UUIDs from the top level down to this zone. |
| `path_code` | STRING | Chain of data-zone codes from the top level down to this zone. |
| `path_name` | STRING | Chain of data-zone names from the top level down to this zone. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `valid_from` | STRING | Date from which the record is valid. |
| `valid_to` | STRING | Date until which the record is valid (NULL = open-ended). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_data_zone.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_data_zone](/initial/raw_derp/crm_data_zone.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY COALESCE(updated_at, created_at) DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `data_zone_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_data_zone`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT data_zone_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_data_zone`
GROUP BY data_zone_id
HAVING n > 1
```

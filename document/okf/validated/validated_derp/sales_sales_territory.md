---
type: BigQuery Table
title: "sales_sales_territory"
description: "One row = one sales territory node from source table `sales_sales_territory`, unique on (sale_territory_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=sales_sales_territory&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: sales_sales_territory
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/sales_sales_territory.sqlx"
    title: "Dataform definition (validated/derp/sales_sales_territory.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of DERP `sales_sales_territory`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Hierarchy of sales territories (up to four levels) with code, name and validity dates.
No other repo object reads it.

# Grain and key

One row per `sale_territory_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `valid_from` | DATE | Date from which the territory is valid. |
| `valid_to` | DATE | Date until which the territory is valid (NULL = open-ended). |
| `company_id` | STRING | UUID of the company that owns the record. |
| `company_code` | STRING | Code of the company that owns the record. |
| `organization_id` | STRING | UUID of the organization that owns the record. |
| `organization_code` | STRING | Code of the organization that owns the record. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/sales_sales_territory.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.sales_sales_territory](/initial/raw_derp/sales_sales_territory.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_territory_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.sales_sales_territory`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_territory_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.sales_sales_territory`
GROUP BY sale_territory_id
HAVING n > 1
```

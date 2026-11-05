---
type: BigQuery Table
title: "unit"
description: "One row = one measurement unit from source table `unit`, unique on (unit_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=unit&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: unit
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/unit.sqlx"
    title: "Dataform definition (validated/mastersku/unit.sqlx)"
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

Validated copy of MASTERSKU `unit`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Lookup of length and weight/volume units used for MASTERSKU product dimensions and weights.
Used by: [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md).

# Grain and key

One row per `unit_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `unit_id` | STRING | Unique identifier (UUID) of the measurement unit. |
| `unit_type_name` | STRING | Unit type in Thai (`ความยาว` = length, `น้ำหนัก` = weight/volume). |
| `unit_name` | STRING | Unit symbol (e.g. `mm`, `cm`, `m`, `inch`, `ft`, `kg`, `g`, `lt`, `ml`). |
| `unit_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `unit_created_date` | DATETIME | Timestamp when the record was created. |
| `unit_updated_date` | DATETIME | Timestamp when the record was last updated. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/unit.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.unit](/initial/raw_mastersku/unit.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `unit_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.unit`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT unit_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.unit`
GROUP BY unit_id
HAVING n > 1
```

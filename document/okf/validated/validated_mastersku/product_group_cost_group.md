---
type: BigQuery Table
title: "product_group_cost_group"
description: "One row = one product group cost-group assignment from source table `product_group_cost_group`, unique on (pgcg_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product_group_cost_group&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: product_group_cost_group
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product_group_cost_group.sqlx"
    title: "Dataform definition (validated/mastersku/product_group_cost_group.sqlx)"
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

Validated copy of MASTERSKU `product_group_cost_group`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Cost groups assigned to each MASTERSKU product group.
No other table or view in this repository reads it.

# Grain and key

One row per `pgcg_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `pgcg_id` | STRING | Unique identifier (UUID) of the cost-group assignment. |
| `pgcg_pg_id` | STRING | Product group (FK to `product_group.pg_id`). |
| `pgcg_cost_group_detail` | STRING | Cost groups assigned to the product group as a JSON array of identifiers. |
| `pgcg_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `pgcg_create_date` | DATETIME | Timestamp when the record was created. |
| `pgcg_create_by` | STRING | Identifier of the user who created the record. |
| `pgcg_update_date` | DATETIME | Timestamp when the record was last updated. |
| `pgcg_update_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product_group_cost_group.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product_group_cost_group](/initial/raw_mastersku/product_group_cost_group.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `pgcg_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 896 rows, 158.3 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product_group_cost_group`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT pgcg_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product_group_cost_group`
GROUP BY pgcg_id
HAVING n > 1
```

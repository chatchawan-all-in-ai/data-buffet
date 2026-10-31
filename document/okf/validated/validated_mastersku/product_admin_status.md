---
type: BigQuery Table
title: "product_admin_status"
description: "One row = one cleaned copy of the source table `product_admin_status`, unique on (pas_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product_admin_status&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: product_admin_status
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product_admin_status.sqlx"
    title: "Dataform definition (validated/mastersku/product_admin_status.sqlx)"
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

Validated copy of MASTERSKU `product_admin_status`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `pas_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `pas_id` | STRING | Meaning not documented in the repo. |
| `pas_name` | STRING | Meaning not documented in the repo. |
| `pas_is_use` | BOOL | Meaning not documented in the repo. |
| `pas_created_date` | DATETIME | Meaning not documented in the repo. |
| `pas_updated_date` | DATETIME | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product_admin_status.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product_admin_status](/initial/raw_mastersku/product_admin_status.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `pas_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 6 rows, 453 B.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product_admin_status`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT pas_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product_admin_status`
GROUP BY pas_id
HAVING n > 1
```

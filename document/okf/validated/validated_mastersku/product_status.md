---
type: BigQuery Table
title: "product_status"
description: "One row = one product status from source table `product_status`, unique on (ps_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product_status&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: product_status
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product_status.sqlx"
    title: "Dataform definition (validated/mastersku/product_status.sqlx)"
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

Validated copy of MASTERSKU `product_status`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Lookup of MASTERSKU product statuses (On, Off, Draft, Pending, Approve, Reject, InActive By Allkons).
No other repo object reads it.

# Grain and key

One row per `ps_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `ps_id` | STRING | Unique identifier (UUID) of the product status. |
| `ps_name` | STRING | Product status name (`On`, `Off`, `Draft`, `Pending`, `Approve`, `Reject`, `InActive By Allkons`). |
| `ps_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `ps_created_date` | DATETIME | Timestamp when the record was created. |
| `ps_updated_date` | DATETIME | Timestamp when the record was last updated. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product_status.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product_status](/initial/raw_mastersku/product_status.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `ps_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product_status`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT ps_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product_status`
GROUP BY ps_id
HAVING n > 1
```

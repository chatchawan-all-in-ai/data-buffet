---
type: BigQuery Table
title: "order_from_allkon_m"
description: "One row = one order received from the Allkons platform (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=order_from_allkon_m&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: order_from_allkon_m
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/order_from_allkon_m.sqlx"
    title: "Dataform definition (validated/mac5/order_from_allkon_m.sqlx)"
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

Validated copy of MAC5 `order_from_allkon_m`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Orders received from the Allkons platform, with promotion type, source and processing statuses.
No other repo object reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Row identifier of the order. |
| `order_no` | STRING | Allkons platform order number (e.g. `QOAG-00158-00048-22-09`). |
| `status` | STRING | Status code of the order row (1, 2, 3). |
| `create_date` | DATETIME | Date and time the order was received. |
| `promotion_type` | STRING | Promotion types applied to the order (e.g. `Premium`, `ComboSet`, `VolumePrice`, comma-separated). |
| `notes` | STRING | Processing notes of the order import, such as confirm status codes or `#order_null`. |
| `sub_order` | STRING | Sub-order number of the order. |
| `made_from` | STRING | Source application that created the order (e.g. `AKM`, `AMRP`). |
| `datetime` | DATETIME | Date and time of the order event. |
| `deliverystatus` | STRING | Delivery status code of the order. |
| `cancelstatus` | STRING | Cancel status code of the order (0, 1, 2). |
| `confirmstatus` | STRING | Confirm status code of the order (0, 1, 2). |
| `order_source` | STRING | Channel the order came from (e.g. `AK Platform`, `BOT (Semi-Auto)`). |
| `is_complete` | INT64 | Completion status code of the order import (0 to 3). |
| `update_date` | DATETIME | Date and time the order row was last updated. |

# How it is built

- Definition: `definitions/validated/mac5/order_from_allkon_m.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.order_from_allkon_m](/initial/raw_mac5_ag01/order_from_allkon_m.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY update_date desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.order_from_allkon_m`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.order_from_allkon_m`
GROUP BY company_id, id
HAVING n > 1
```

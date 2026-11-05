---
type: BigQuery Table
title: "product_detail_bot_re"
description: "One row = one component of a developer article (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=product_detail_bot_re&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: product_detail_bot_re
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/product_detail_bot_re.sqlx"
    title: "Dataform definition (validated/mac5/product_detail_bot_re.sqlx)"
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

Validated copy of MAC5 `product_detail_bot_re`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: MAC5 stock items and quantities that make up each developer article of the real-estate PO bot.
No other repo object reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Row identifier of the component line. |
| `product_id` | INT64 | Identifier of the developer article this component belongs to (`product_bot_re.id`). |
| `sku_id` | STRING | MAC5 stock code of the component product. |
| `qty` | FLOAT64 | Quantity of the component per article. |
| `channel` | STRING | Developer group of the article (e.g. `AP`, `SANSIRI`, `Frasers`, `QH`). |
| `create_date` | DATETIME | Date and time the row was created. |

# How it is built

- Definition: `definitions/validated/mac5/product_detail_bot_re.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.product_detail_bot_re](/initial/raw_mac5_ag01/product_detail_bot_re.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY create_date desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.product_detail_bot_re`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.product_detail_bot_re`
GROUP BY company_id, id
HAVING n > 1
```

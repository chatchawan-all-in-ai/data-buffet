---
type: BigQuery Table
title: "product_bot_re"
description: "One row = one developer article (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=product_bot_re&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: product_bot_re
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/product_bot_re.sqlx"
    title: "Dataform definition (validated/mac5/product_bot_re.sqlx)"
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

Validated copy of MAC5 `product_bot_re`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Developer article (SKU) codes used on real-estate purchase orders, with type, price and developer group, for the real-estate PO bot.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Row identifier of the developer product. |
| `sku_id` | STRING | Developer article (SKU) code as printed on its purchase orders. |
| `qty` | FLOAT64 | Quantity per article. |
| `price` | FLOAT64 | Agreed price of the article. |
| `channel` | STRING | Developer group of the article (e.g. `AP`, `SANSIRI`, `SC`, `Frasers`, `QH`). |
| `type_product` | STRING | Article type (`NORMAL` = single product, `COMBOSET` = set of several MAC5 products). |
| `create_date` | DATETIME | Date and time the row was created. |

# How it is built

- Definition: `definitions/validated/mac5/product_bot_re.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.product_bot_re](/initial/raw_mac5_ag01/product_bot_re.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY create_date desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 277 rows, 16.8 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.product_bot_re`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.product_bot_re`
GROUP BY company_id, id
HAVING n > 1
```

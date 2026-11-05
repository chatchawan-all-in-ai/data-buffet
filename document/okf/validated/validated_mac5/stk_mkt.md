---
type: BigQuery Table
title: "stk_mkt"
description: "One row = one product with its marketing attributes (per company), unique on (company_id, stkcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stk_mkt&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: stk_mkt
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stk_mkt.sqlx"
    title: "Dataform definition (validated/mac5/stk_mkt.sqlx)"
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

Validated copy of MAC5 `stk_mkt`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Marketing attributes of products (production type, segment, series, size, colour).
No other repo object reads it.

# Grain and key

One row per `company_id`, `stkcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `stkcode` | STRING | Product (stock item) code. |
| `stkgroup` | STRING | Stock group code (joins `stg.stgcode`). |
| `stkdesct1` | STRING | Thai product description, line 1. |
| `zgroup1` | STRING | Marketing group, level 1. |
| `zgroup2` | STRING | Marketing group, level 2. |
| `zsize` | STRING | Size label of the product (e.g. 3000 litres, 3.0Q). |
| `zcolor` | STRING | Colour of the product (e.g. GRAY, BLACK, NATURAL). |
| `zgroup3` | STRING | Product category name in Thai (e.g. treatment tank). |
| `zgroup4` | STRING | Marketing group, level 4 (e.g. `OK`). |
| `zgroup5` | STRING | Production or sourcing type (e.g. SOURCING, FRP, ROTO, BLOW, INJECTION, SERVICE). |
| `zgroup6` | STRING | Marketing segment as a numeric code plus Thai name (e.g. `0301030201` exterior paint). |
| `zgroup7` | STRING | Product series or brand line (e.g. LITETITE, Z Series). |

# How it is built

- Definition: `definitions/validated/mac5/stk_mkt.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.stk_mkt](/initial/raw_mac5_ag01/stk_mkt.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stkdesct1 DESC) = 1`.
- Storage: not partitioned; cluster by `company_id`, `stkcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stk_mkt`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stkcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stk_mkt`
GROUP BY company_id, stkcode
HAVING n > 1
```

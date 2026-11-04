---
type: BigQuery Table
title: "stg"
description: "One row = one stock group (per company), unique on (company_id, stgcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stg&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: stg
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stg.sqlx"
    title: "Dataform definition (validated/mac5/stg.sqlx)"
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

Validated copy of MAC5 `stg` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Stock group master with Thai/English names and the mapped accounting product group.
Used by: [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md).

# Grain and key

One row per `company_id`, `stgcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `stgcode` | STRING | Stock group code. |
| `stgdesct` | STRING | Thai name of the stock group. |
| `stgdesce` | STRING | English name or type label of the stock group. |
| `gacccode` | STRING | Accounting product group code of the stock group (from `stgacc`). |
| `gaccname` | STRING | Accounting product group name of the stock group (from `stgacc`). |

# How it is built

- Definition: `definitions/validated/mac5/stg.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [validated_mac5.stgacc](/validated/validated_mac5/stgacc.md), [validated_mac5.stg_report](/validated/validated_mac5/stg_report.md), [raw_mac5_ag01.stg](/initial/raw_mac5_ag01/stg.md), [raw_mac5_aa05.stg](/initial/raw_mac5_aa05/stg.md), [raw_mac5_ab01.stg](/initial/raw_mac5_ab01/stg.md), [raw_mac5_ac02.stg](/initial/raw_mac5_ac02/stg.md), [raw_mac5_ak02.stg](/initial/raw_mac5_ak02/stg.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stgdesct desc, stgdesce desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `stgcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stg`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stgcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stg`
GROUP BY company_id, stgcode
HAVING n > 1
```

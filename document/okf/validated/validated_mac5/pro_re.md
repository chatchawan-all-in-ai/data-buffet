---
type: BigQuery Table
title: "pro_re"
description: "One row = one product in an RE-channel promotion (per company), unique on (company_id, proreid, prorestkcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=pro_re&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: pro_re
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/pro_re.sqlx"
    title: "Dataform definition (validated/mac5/pro_re.sqlx)"
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

Validated copy of MAC5 `pro_re`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Products included in RE-channel promotions of the MAC5 ERP, with period and region.
No other repo object reads it.

# Grain and key

One row per `company_id`, `proreid`, `prorestkcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `proreid` | INT64 | Running ID of the promotion item row. |
| `prorestkcode` | STRING | Stock (product) code included in the promotion. |
| `proresttcode` | STRING | Promotion set code the product belongs to (numeric, e.g. `80164`). |
| `prorestt` | STRING | Promotion item status flag (`y` = active). |
| `prorestrdate` | DATE | Start date of the promotion period. |
| `proreenddate` | DATE | End date of the promotion period. |
| `proreregion` | STRING | Region the promotion applies to (`ALL` = all regions). |
| `dinsert` | DATETIME | Date and time the row was inserted. |

# How it is built

- Definition: `definitions/validated/mac5/pro_re.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.pro_re](/initial/raw_mac5_ag01/pro_re.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY proreenddate desc, prorestrdate desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `proreid`, `prorestkcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.pro_re`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, proreid, prorestkcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.pro_re`
GROUP BY company_id, proreid, prorestkcode
HAVING n > 1
```

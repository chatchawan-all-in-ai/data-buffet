---
type: BigQuery Table
title: "pro_crc"
description: "One row = one product in a CRC-channel promotion (per company), unique on (company_id, id, procrcstkcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=pro_crc&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: pro_crc
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/pro_crc.sqlx"
    title: "Dataform definition (validated/mac5/pro_crc.sqlx)"
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

Validated copy of MAC5 `pro_crc`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Products included in CRC-channel promotions of the MAC5 ERP, with promotion set code, period and region.
No other repo object reads it.

# Grain and key

One row per `company_id`, `id`, `procrcstkcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Running ID of the promotion item row. |
| `procrcstkcode` | STRING | Stock (product) code included in the promotion. |
| `procrcsttcode` | STRING | Promotion set code the product belongs to (numeric, e.g. `80164`). |
| `procrcstt` | STRING | Promotion item status flag (`y` = active). |
| `procrcstrdate` | DATE | Start date of the promotion period. |
| `procrcenddate` | DATE | End date of the promotion period. |
| `procrcregion` | STRING | Region the promotion applies to (`ALL` = all regions). |
| `dinsert` | DATETIME | Date and time the row was inserted. |

# How it is built

- Definition: `definitions/validated/mac5/pro_crc.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.pro_crc](/initial/raw_mac5_ag01/pro_crc.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY procrcenddate desc, procrcstrdate desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`, `procrcstkcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.pro_crc`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, procrcstkcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.pro_crc`
GROUP BY company_id, id, procrcstkcode
HAVING n > 1
```

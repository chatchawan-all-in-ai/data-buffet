---
type: BigQuery Table
title: "stg_report"
description: "One row = one product group (per company), unique on (company_id, stgcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stg_report&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: stg_report
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stg_report.sqlx"
    title: "Dataform definition (validated/mac5/stg_report.sqlx)"
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

Validated copy of MAC5 `stg_report`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product (stock) groups used for reporting, with Thai and English names.
Used by: [validated_mac5.stg](/validated/validated_mac5/stg.md).

# Grain and key

One row per `company_id`, `stgcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `stgcode` | STRING | Product (stock) group code. |
| `stgdesct` | STRING | Product group name in Thai. |
| `stgdesce` | STRING | Product group name in English. |
| `stgacccode` | STRING | Account code of the product group. |

# How it is built

- Definition: `definitions/validated/mac5/stg_report.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.stg_report](/initial/raw_mac5_ag01/stg_report.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stgdesct desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `stgcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stg_report`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stgcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stg_report`
GROUP BY company_id, stgcode
HAVING n > 1
```

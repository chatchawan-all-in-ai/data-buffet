---
type: BigQuery Table
title: "stf"
description: "One row = one component line of a product formula (per company), unique on (company_id, stfcode, stflist)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stf&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: stf
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stf.sqlx"
    title: "Dataform definition (validated/mac5/stf.sqlx)"
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

Validated copy of MAC5 `stf`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product formulas (bills of material): components and quantities per finished item.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `stfcode`, `stflist`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `stfcode` | STRING | Product code of the finished item the formula belongs to. |
| `stflist` | STRING | Stock code of the component in the formula. |
| `stfquan` | FLOAT64 | Quantity of the component per finished item. |
| `stfunit` | INT64 | Unit number of the component quantity. |
| `stfautono` | INT64 | Running ID of the formula line. |
| `stfmemo` | STRING | Free-text memo on the formula line. |

# How it is built

- Definition: `definitions/validated/mac5/stf.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.stf](/initial/raw_mac5_ag01/stf.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: not partitioned; cluster by `company_id`, `stfcode`, `stflist`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stf`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stfcode, stflist, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stf`
GROUP BY company_id, stfcode, stflist
HAVING n > 1
```

---
type: BigQuery Table
title: "std"
description: "One row = one customer item-code mapping (per company), unique on (company_id, stdautono)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=std&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: std
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/std.sqlx"
    title: "Dataform definition (validated/mac5/std.sqlx)"
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

Validated copy of MAC5 `std`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Mapping of products to the item codes and descriptions used by specific customers.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `stdautono`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `stdcode` | STRING | Item code the customer uses for the product. |
| `stdtype` | INT64 | Mapping type code (1, 2). |
| `stddebtor` | STRING | Customer code the mapping belongs to (joins `deb.debcode`). |
| `stdstkcode` | STRING | Stock code of the product (joins `stk.stkcode`). |
| `stddesct1` | STRING | Thai description of the item for this customer. |
| `stddesce1` | STRING | English description of the item for this customer. |
| `stdautono` | INT64 | Running ID of the mapping row. |

# How it is built

- Definition: `definitions/validated/mac5/std.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.std](/initial/raw_mac5_ag01/std.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stddesct1 desc, stddesce1 desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `stdautono`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.std`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stdautono, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.std`
GROUP BY company_id, stdautono
HAVING n > 1
```

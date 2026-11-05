---
type: BigQuery Table
title: "tbook_apptype"
description: "One row = one product-line approval type (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_apptype&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbook_apptype
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_apptype.sqlx"
    title: "Dataform definition (validated/mac5/tbook_apptype.sqlx)"
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

Validated copy of MAC5 `tbook_apptype`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product-line approval types of the quotation app, with the approver, position and signature image.
No other repo object reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Approval type identifier, referenced by `tbook_quotation.apptype`. |
| `iddesc` | STRING | Product-line code of the approval type (e.g. `PE`, `PUMP`, `RP`, `LYNN`, `CL`, `AIR`). |
| `idcode` | STRING | Employee code of the approver for the product line. |
| `name` | STRING | Name of the approver for the product line. |
| `dep` | STRING | Position title of the approver. |
| `pic` | STRING | Path of the approver signature image. |

# How it is built

- Definition: `definitions/validated/mac5/tbook_apptype.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_apptype](/initial/raw_mac5_ag01/tbook_apptype.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY iddesc desc, name desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_apptype`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbook_apptype`
GROUP BY company_id, id
HAVING n > 1
```

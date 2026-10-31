---
type: BigQuery Table
title: "ttrip_document"
description: "One row = one documents on a delivery trip, unique on (company_id, frun, fdocument, fserial_no)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=ttrip_document&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/ttrip_document.sqlx"
    title: "Dataform definition (validated/mac5/ttrip_document.sqlx)"
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

Validated copy of MAC5 `ttrip_document`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: documents on a delivery trip. Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_delivery](/dimension/dim_delivery.md), [fact_table.fact_delivery](/fact/fact_delivery.md).

# Grain and key

One row per `company_id`, `frun`, `fdocument`, `fserial_no`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `frun` | STRING | Meaning not documented in the repo. |
| `fmaster` | STRING | Meaning not documented in the repo. |
| `fdocument` | STRING | Meaning not documented in the repo. |
| `fserial_no` | STRING | Meaning not documented in the repo. |
| `fitem` | STRING | Meaning not documented in the repo. |
| `fusername` | STRING | Meaning not documented in the repo. |
| `fdatetime` | STRING | Meaning not documented in the repo. |
| `fitem2` | STRING | Meaning not documented in the repo. |
| `fdoc_type` | STRING | Meaning not documented in the repo. |
| `fcancel` | STRING | Likely cancel flag (inferred from the column name only; not documented in the repo). |
| `fref1` | STRING | Meaning not documented in the repo. |
| `fdocument_rt` | INT64 | Meaning not documented in the repo. |
| `fdocument_rtdate` | DATETIME | Meaning not documented in the repo. |
| `fdocument_ac` | INT64 | Meaning not documented in the repo. |
| `fdocument_acdate` | DATETIME | Meaning not documented in the repo. |
| `frepro` | STRING | Meaning not documented in the repo. |
| `fqty_order` | INT64 | Meaning not documented in the repo. |
| `fitemdoc` | STRING | Meaning not documented in the repo. |
| `fitem3` | STRING | Meaning not documented in the repo. |
| `fprice` | FLOAT64 | Likely price (inferred from the column name only; not documented in the repo). |
| `fin365` | INT64 | Meaning not documented in the repo. |
| `im_mac` | STRING | Meaning not documented in the repo. |
| `post` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/ttrip_document.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.ttrip_document](/initial/raw_mac5_ag01/ttrip_document.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY fdatetime desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `frun`, `fdocument`, `fserial_no`.
- Approximate size (BigQuery metadata, 2026-10-31): 12,360,420 rows, 1.9 GB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.ttrip_document`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, frun, fdocument, fserial_no, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.ttrip_document`
GROUP BY company_id, frun, fdocument, fserial_no
HAVING n > 1
```

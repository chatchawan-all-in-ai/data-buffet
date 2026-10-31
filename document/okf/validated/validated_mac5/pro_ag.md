---
type: BigQuery Table
title: "pro_ag"
description: "One row = one promotion (AG), unique on (company_id, proagid, proagstkcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=pro_ag&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/pro_ag.sqlx"
    title: "Dataform definition (validated/mac5/pro_ag.sqlx)"
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

Validated copy of MAC5 `pro_ag`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: promotion (AG). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `proagid`, `proagstkcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `proagid` | INT64 | Meaning not documented in the repo. |
| `proagstkcode` | STRING | Meaning not documented in the repo. |
| `proagsttcode` | STRING | Meaning not documented in the repo. |
| `proagstt` | STRING | Meaning not documented in the repo. |
| `proagstrdate` | DATE | Meaning not documented in the repo. |
| `proagenddate` | DATE | Meaning not documented in the repo. |
| `proagregion` | STRING | Meaning not documented in the repo. |
| `dinsert` | DATETIME | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/pro_ag.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.pro_ag](/initial/raw_mac5_ag01/pro_ag.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY proagenddate desc, proagstrdate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `proagid`, `proagstkcode`.
- Approximate size (BigQuery metadata, 2026-10-31): 250 rows, 17.9 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.pro_ag`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, proagid, proagstkcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.pro_ag`
GROUP BY company_id, proagid, proagstkcode
HAVING n > 1
```

---
type: BigQuery Table
title: "ap_s"
description: "One row = one AP document status (per company), unique on (company_id, ap_scode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=ap_s&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: ap_s
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/ap_s.sqlx"
    title: "Dataform definition (validated/mac5/ap_s.sqlx)"
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

Validated copy of MAC5 `ap_s` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Status codes and display names (with colours) for purchase-side documents, referenced by `mihstatus`.
Used by: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md).

# Grain and key

One row per `company_id`, `ap_scode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `ap_scode` | INT64 | AP (purchase) document status code, referenced by `mihstatus` of purchase documents. |
| `ap_snamet` | STRING | Thai status name. |
| `ap_snamee` | STRING | English status name (often the same Thai text). |
| `ap_scolf` | INT64 | Foreground (text) colour of the status in the ERP, as a Windows RGB integer. |
| `ap_scolb` | INT64 | Background colour of the status in the ERP, as a Windows RGB integer. |

# How it is built

- Definition: `definitions/validated/mac5/ap_s.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.ap_s](/initial/raw_mac5_ag01/ap_s.md), [raw_mac5_aa05.ap_s](/initial/raw_mac5_aa05/ap_s.md), [raw_mac5_ab01.ap_s](/initial/raw_mac5_ab01/ap_s.md), [raw_mac5_ac02.ap_s](/initial/raw_mac5_ac02/ap_s.md), [raw_mac5_ak02.ap_s](/initial/raw_mac5_ak02/ap_s.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ap_snamet desc, ap_snamee desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `ap_scode`.
- Approximate size (BigQuery metadata, 2026-10-31): 405 rows, 17.0 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.ap_s`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, ap_scode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.ap_s`
GROUP BY company_id, ap_scode
HAVING n > 1
```

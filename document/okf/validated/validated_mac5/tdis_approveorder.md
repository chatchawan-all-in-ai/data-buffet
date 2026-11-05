---
type: BigQuery Table
title: "tdis_approveorder"
description: "One row = one order approval (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tdis_approveorder&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tdis_approveorder
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tdis_approveorder.sqlx"
    title: "Dataform definition (validated/mac5/tdis_approveorder.sqlx)"
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

Validated copy of MAC5 `tdis_approveorder`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Approvals that turn quotation-app pre-orders into MAC5 sales orders, with the keying user, approver and time.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Row identifier of the approval. |
| `preorder` | STRING | Pre-order number from the quotation app (T-prefixed, e.g. `TAR63041193`). |
| `orderno` | STRING | MAC5 sales order number created from the pre-order. |
| `userkey` | STRING | Employee code of the user who keyed the order. |
| `userapprove` | STRING | Code of the user who approved the order. |
| `datetime` | DATETIME | Date and time of the approval. |

# How it is built

- Definition: `definitions/validated/mac5/tdis_approveorder.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tdis_approveorder](/initial/raw_mac5_ag01/tdis_approveorder.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY datetime desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tdis_approveorder`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tdis_approveorder`
GROUP BY company_id, id
HAVING n > 1
```

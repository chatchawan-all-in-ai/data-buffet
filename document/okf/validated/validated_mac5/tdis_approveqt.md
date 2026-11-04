---
type: BigQuery Table
title: "tdis_approveqt"
description: "One row = one quotation approval request per product line (per company), unique on (company_id, docno, stktype)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tdis_approveqt&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tdis_approveqt
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tdis_approveqt.sqlx"
    title: "Dataform definition (validated/mac5/tdis_approveqt.sqlx)"
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

Validated copy of MAC5 `tdis_approveqt`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Approval requests of quotations per product-line approval type, with approval results, users, dates and notes per level.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `docno`, `stktype`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `docno` | STRING | Quotation identifier (`tbook_quotation.id`) sent for approval. |
| `lv1` | STRING | Level-1 approval result code. |
| `lv2` | STRING | Level-2 approval result code. |
| `lv3` | STRING | Level-3 approval result code (1, 2, 0). |
| `note1` | STRING | Level-1 approval note. |
| `note2` | STRING | Level-2 approval note. |
| `note3` | STRING | Level-3 approval note. |
| `u1` | STRING | User who acted at approval level 1. |
| `u2` | STRING | User who acted at approval level 2. |
| `u3` | STRING | Employee code of the user who acted at approval level 3. |
| `d1` | STRING | Date and time of the level-1 approval (text). |
| `d2` | STRING | Date and time of the level-2 approval (text). |
| `d3` | STRING | Date and time of the level-3 approval (text). |
| `sendto` | STRING | Sent-for-approval flag (1 = sent). |
| `sendtime` | STRING | Date the quotation was sent for approval (text). |
| `comment` | STRING | Sales comment attached to the approval request, such as delivery instructions. |
| `stktype` | STRING | Product-line approval type code (`tbook_apptype.iddesc`, e.g. `PE`, `PUMP`, `RP`). |

# How it is built

- Definition: `definitions/validated/mac5/tdis_approveqt.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tdis_approveqt](/initial/raw_mac5_ag01/tdis_approveqt.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY sendtime desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `docno`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tdis_approveqt`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, docno, stktype, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tdis_approveqt`
GROUP BY company_id, docno, stktype
HAVING n > 1
```

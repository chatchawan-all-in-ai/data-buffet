---
type: BigQuery Table
title: "curated_journal_invoice"
description: "One row = one DERP inventory movement journal (name IM-MAC-01) with the MAC5 document number parsed from its description and the match status against curated_mih, unique on journalNumber."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_derp&t=curated_journal_invoice&page=table"
project_id: databuffet-nonprd
dataset_id: curated_derp
table_id: curated_journal_invoice
tags: ["curated", "curated_derp", "derp", "DERP"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/derp/curated_journal_invoice.sqlx"
    title: "Dataform definition (curated/derp/curated_journal_invoice.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

DERP (Dynamics 365) inventory movement journals of journal name `IM-MAC-01` (the stock movements posted for MAC5 documents), each tied to the MAC5 document it belongs to. The document number is parsed out of the journal description and looked up in [curated_mih](/curated/curated_mac5/curated_mih.md); the journal cost is the negated sum of its entry `cost_amount`.

Read by: [curated_invoice_line_cost](/curated/curated_derp/curated_invoice_line_cost.md).

# Grain and key

One row = one journal: key `journalNumber` (the header table `inventory_movement_journal_headers` is unique on `journal_number`; only `journal_name_id = 'IM-MAC-01'` is kept). No declared `uniqueKey`. `company_id`, `mihType` and `mihVnos` are filled only when exactly one `curated_mih` document carries the parsed number; otherwise they are NULL.

# Schema

| Column | Type | Description |
|---|---|---|
| `journalNumber` | STRING | Journal number (`journal_number` of the DERP journal header); key. |
| `journalDescription` | STRING | Journal description text (`description`), cleaned with `cleanString`. |
| `docNo` | STRING | MAC5 document number parsed from the description by regular expression. For a description that starts with a date (d/m/y) and contains the word 'คืน', the return-document number (`RT...-...` followed by 6 or more digits) is taken first, else the first letters+6-or-more-digit token; for other descriptions the number must follow an optional prefix (`รับคืน`, `อ้างอิงใบจ่าย`, `ใบจ่ายขายจาก`, `ใบจ่ายขายจาก MAC-5`) at the start. Letters in front of the digits are part of the number. NULL when no number is found. |
| `matchStatus` | STRING | Result of matching `docNo` to `curated_mih.mihVnos`: `NO_DOC_NO` (`docNo` is NULL), `NOT_IN_MAC5` (no document with that number), `AMBIGUOUS` (more than one document across companies/types has that number), `RETURN` (unique match and the journal is a return: description prefix `รับคืน`, or a dated return description), `MATCHED` (unique match, not a return). |
| `company_id` | STRING | Company code of the matched MAC5 document; NULL unless exactly one document matches (`RETURN` and `MATCHED` rows). |
| `mihType` | STRING | Document type of the matched MAC5 document; NULL unless exactly one document matches. |
| `mihVnos` | STRING | Document number of the matched MAC5 document; NULL unless exactly one document matches. |
| `isPosted` | BOOL | Boolean posting flag passed through from the [validated journal header](/validated/validated_derp/inventory_movement_journal_headers.md#schema) `is_posted`. |
| `postedDatetime` | DATETIME | Posting time in Asia/Bangkok, passed through from the [validated journal header](/validated/validated_derp/inventory_movement_journal_headers.md#schema) `posted_datetime`. |
| `journalCost` | FLOAT64 | Negated sum of `cost_amount` over the journal's entries in `inventory_movement_journal_entries`; NULL when the journal has no entries. |
| `journalLines` | INT64 | Number of entry lines of the journal; 0 when it has none. |

# How it is built

- Definition: `definitions/curated/derp/curated_journal_invoice.sqlx` (`type: "table"`, tags `curated`).
- Storage options: `{"clusterBy": ["matchStatus", "mihVnos"]}`.
- Reads: [validated_derp.inventory_movement_journal_headers](/validated/validated_derp/inventory_movement_journal_headers.md), [validated_derp.inventory_movement_journal_entries](/validated/validated_derp/inventory_movement_journal_entries.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md).
- Document match: `curated_mih` grouped by `mihVnos` (one row per number with `company_id`, `mihType` and a document count), joined to the journal on `mihVnos = docNo`.
- Full rebuild (`type: "table"`, tag `curated`); runs after `curated_schema_derp`.

# Examples

Journals per match status.

```sql
SELECT matchStatus, COUNT(*) AS n, SUM(journalCost) AS total_cost
FROM `databuffet-nonprd.curated_derp.curated_journal_invoice`
GROUP BY matchStatus
ORDER BY n DESC
```

Posted journals matched to one MAC5 invoice.

```sql
SELECT journalNumber, postedDatetime, journalCost, journalLines
FROM `databuffet-nonprd.curated_derp.curated_journal_invoice`
WHERE matchStatus = 'MATCHED' AND isPosted
  AND company_id = 'ag01' AND mihType = 'IS' AND mihVnos = 'REPLACE_WITH_DOCUMENT_NUMBER'
```

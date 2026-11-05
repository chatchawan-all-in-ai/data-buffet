---
type: BigQuery Table
title: "pathfilestamper"
description: "One row = one file attached to an order (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=pathfilestamper&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: pathfilestamper
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/pathfilestamper.sqlx"
    title: "Dataform definition (validated/mac5/pathfilestamper.sqlx)"
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

Validated copy of MAC5 `pathfilestamper`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Files attached to quotation-app orders (POs, pay-in slips, maps, delivery proofs), with file share paths and payment notes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Row identifier of the file record. |
| `mainqtid` | INT64 | Quotation spread identifier (`main_qtspread.id`). |
| `preorderno` | STRING | Pre-order number from the quotation app (T-prefixed). |
| `orderno` | STRING | MAC5 sales order number the file belongs to. |
| `type` | STRING | File type (`PO`, `Payin`, `Map`, `Delivery`, `MEMO`, `BOQ`, `Other`). |
| `path212` | STRING | Path of the file on the web upload server. |
| `path10acc` | STRING | Path of the file on the accounting file share. |
| `path10fac` | STRING | Path of the file on the factory admin file share. |
| `filename` | STRING | File name (e.g. `<order>-PAYIN.pdf`). |
| `uinsert` | STRING | Employee code of the user who uploaded the file, or `bot`. |
| `date` | STRING | Date and time the file was uploaded (text). |
| `status` | INT64 | Active flag (1 = active). |
| `pathqtid` | STRING | Identifier of the quotation-app record the file was uploaded under. |
| `note` | STRING | Payment note of the file (e.g. 100 percent transfer, 30 percent deposit). |
| `datepayinadmin` | DATE | Date the pay-in was confirmed by the admin. |
| `refpo` | STRING | Customer purchase order reference. |

# How it is built

- Definition: `definitions/validated/mac5/pathfilestamper.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.pathfilestamper](/initial/raw_mac5_ag01/pathfilestamper.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY datepayinadmin desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.pathfilestamper`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.pathfilestamper`
GROUP BY company_id, id
HAVING n > 1
```

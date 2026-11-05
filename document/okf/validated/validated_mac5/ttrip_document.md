---
type: BigQuery Table
title: "ttrip_document"
description: "One row = one scanned item unit loaded on a delivery trip (per company), unique on (company_id, frun, fdocument, fserial_no)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=ttrip_document&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: ttrip_document
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `ttrip_document`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Item scans of delivery documents loaded on trips, linking each scanned unit to its trip and MAC5 delivery document; source of dim_delivery and fact_delivery.

Read by: [dimension_table.dim_delivery](/dimension/dim_delivery.md), [fact_table.fact_delivery](/fact/fact_delivery.md).

# Grain and key

One row per `company_id`, `frun`, `fdocument`, `fserial_no`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `frun` | STRING | Scan record identifier (timestamp `yyMMddHHmmss` plus sequence). |
| `fmaster` | STRING | Trip identifier (`ttrip.frun`). |
| `fdocument` | STRING | MAC5 delivery document number loaded on the trip (matches `mil.milvnos` of type IS). |
| `fserial_no` | STRING | Scanned serial or barcode of the unit. |
| `fitem` | STRING | Stock code of the scanned item. |
| `fusername` | STRING | Code of the user who scanned the item. |
| `fdatetime` | STRING | Date and time the item was scanned (`yyyyMMddHHmmss`). |
| `fitem2` | STRING | Alternative stock code of the scanned item, used when `fitem` does not match the invoice line. |
| `fdoc_type` | STRING | Document type of `fdocument` (e.g. `IS`). |
| `fcancel` | STRING | Customer refusal flag (0 = received, other = refused). |
| `fref1` | STRING | Sales order number referenced by the delivery document. |
| `fdocument_rt` | INT64 | Document returned flag. |
| `fdocument_rtdate` | DATETIME | Date the document was returned. |
| `fdocument_ac` | INT64 | Document received by accounting flag. |
| `fdocument_acdate` | DATETIME | Date the document was received by accounting. |
| `frepro` | STRING | Reprocess reference of the scan. |
| `fqty_order` | INT64 | Ordered quantity of the item on the document. |
| `fitemdoc` | STRING | Item reference of the document line. |
| `fitem3` | STRING | Third stock code or barcode of the scanned item. |
| `fprice` | FLOAT64 | Price value of the scanned item. |
| `fin365` | INT64 | IN365 flag of the scan. |
| `im_mac` | STRING | Device (MAC) identifier of the scanner. |
| `post` | STRING | Posting flag of the scan. |

# How it is built

- Definition: `definitions/validated/mac5/ttrip_document.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.ttrip_document](/initial/raw_mac5_ag01/ttrip_document.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY fdatetime desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `frun`, `fdocument`, `fserial_no`.

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

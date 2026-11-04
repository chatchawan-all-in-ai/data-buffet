---
type: BigQuery Table
title: "tempgpsweb"
description: "One row = one delivered item on one delivery document from source table `tempgpsweb` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tempgpsweb&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tempgpsweb
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tempgpsweb.sqlx"
    title: "Dataform definition (validated/mac5/tempgpsweb.sqlx)"
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

Validated copy of MAC5 `tempgpsweb`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Delivery tracking rows from the GPS web app: document, vehicle, item, quantity and loading/release/receipt status.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `fdocument` | STRING | Document number of the delivery (e.g. invoice number). |
| `fserial_no` | STRING | Serial or reference document number of the delivery. |
| `fcode` | STRING | Delivery job code. |
| `fvehicle` | STRING | Registration plate of the delivery vehicle. |
| `fitem` | STRING | Product code or barcode of the delivered item. |
| `fitem2` | STRING | Alternate product code or barcode of the delivered item. |
| `qty2` | INT64 | Quantity of the item delivered. |
| `s1` | STRING | Loading status text in Thai (goods loaded onto the truck). |
| `s2` | STRING | Truck release status text in Thai (truck released or not released). |
| `s3` | STRING | Receipt status text in Thai (goods received or not yet delivered). |
| `stt` | STRING | Status code of the delivery row (1, 2). |
| `username` | STRING | User code of the person who recorded the row. |

# How it is built

- Definition: `definitions/validated/mac5/tempgpsweb.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tempgpsweb](/initial/raw_mac5_ag01/tempgpsweb.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tempgpsweb`
LIMIT 100
```

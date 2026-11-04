---
type: BigQuery Table
title: "tdelivery"
description: "One row = one delivery confirmation of a document on a trip (per company), unique on (company_id, frun)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tdelivery&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tdelivery
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tdelivery.sqlx"
    title: "Dataform definition (validated/mac5/tdelivery.sqlx)"
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

Validated copy of MAC5 `tdelivery`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Delivery confirmations of MAC5 delivery documents on trips, with GPS position, place name and zone.
Used by: [dimension_table.dim_delivery](/dimension/dim_delivery.md), [fact_table.fact_delivery](/fact/fact_delivery.md).

# Grain and key

One row per `company_id`, `frun`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `frun` | STRING | Delivery record identifier. |
| `fmaster` | STRING | Trip identifier (`ttrip.frun`). |
| `fserial_no` | STRING | MAC5 delivery document number confirmed as delivered (matches `mil.milvnos`). |
| `fdatetime` | STRING | Date and time of the delivery confirmation (`yyyyMMddHHmmss`). |
| `flattitude` | STRING | Latitude of the delivery point. |
| `flongtitude` | STRING | Longitude of the delivery point. |
| `fpoi` | STRING | Place name of the delivery point from reverse geocoding. |
| `fzone` | STRING | Delivery zone name (e.g. `ZONE สีส้ม`). |
| `fvat` | STRING | VAT flag of the delivery. |
| `freceive` | STRING | Received flag of the delivery. |
| `fdocument` | STRING | Document number of the delivery. |
| `flatd` | STRING | Latitude of the delivery point as digits without the decimal point. |
| `flongd` | STRING | Longitude of the delivery point as digits without the decimal point. |

# How it is built

- Definition: `definitions/validated/mac5/tdelivery.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tdelivery](/initial/raw_mac5_ag01/tdelivery.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY fdatetime desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `frun`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tdelivery`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, frun, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tdelivery`
GROUP BY company_id, frun
HAVING n > 1
```

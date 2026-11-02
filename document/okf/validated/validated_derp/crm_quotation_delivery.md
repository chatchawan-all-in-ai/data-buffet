---
type: BigQuery Table
title: "crm_quotation_delivery"
description: "One row = one delivery round of a quotation from source table `crm_quotation_delivery`, unique on (quotation_delivery_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_quotation_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_quotation_delivery
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_quotation_delivery.sqlx"
    title: "Dataform definition (validated/derp/crm_quotation_delivery.sqlx)"
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

Validated copy of DERP `crm_quotation_delivery`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Planned delivery rounds of quotations: ship date, time window, receiver and delivery address.
No other table or view in this repository reads it.

# Grain and key

One row per `quotation_delivery_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_delivery_id` | STRING | UUID of the quotation delivery round. |
| `quotation_id` | STRING | UUID of the quotation in `crm_quotation`. |
| `quotation_no` | STRING | Quotation document number (e.g. `QT2607...` or `MDT2610...`). |
| `quotation_date` | DATE | Quotation document date. |
| `round_no` | INT64 | Delivery round number within the quotation (1, 2, ...). |
| `ship_date` | DATETIME | Planned ship date and time of the delivery round. |
| `time_start` | STRING | Start of the delivery time window (`HH:MM:SS`). |
| `time_end` | STRING | End of the delivery time window (`HH:MM:SS`). |
| `receiver_name` | STRING | Name of the person receiving the delivery. |
| `phone` | STRING | Phone number of the delivery receiver. |
| `ship_type` | STRING | Shipping type code of the delivery round (`0` or `1`). |
| `address_full` | STRING | Full delivery address as one text string. |
| `address_detail` | STRING | Delivery address detail line. |
| `sub_district_code` | STRING | Sub-district code (6-digit Thai administrative code). |
| `sub_district` | STRING | Sub-district (tambon or khwaeng) name. |
| `district_code` | STRING | District code (4-digit Thai administrative code). |
| `district` | STRING | District (amphoe or khet) name. |
| `province_code` | STRING | Province code (2-digit Thai administrative code). |
| `province` | STRING | Province name. |
| `postal_code` | STRING | Postal code. |
| `country_code` | STRING | Country code (ISO 3166 alpha-3, e.g. `THA`). |
| `phase` | STRING | Phase (project stage) of the delivery address. |
| `house_no` | STRING | House number of the delivery address. |
| `plot` | STRING | Plot (land lot) number of the delivery address. |
| `remark_logistic` | STRING | Remark for the logistics team. |
| `latitude` | FLOAT64 | Latitude of the location in decimal degrees. |
| `longitude` | FLOAT64 | Longitude of the location in decimal degrees. |
| `customer_address_id` | STRING | UUID of the customer address in `crm_customer_address` used for the delivery. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `map_url` | STRING | Map link (e.g. Google Maps URL) of the location. |
| `nearby_landmark` | STRING | Nearby landmark of the delivery address. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_quotation_delivery.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_quotation_delivery](/initial/raw_derp/crm_quotation_delivery.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `quotation_delivery_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,109 rows, 1.4 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_quotation_delivery`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT quotation_delivery_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_quotation_delivery`
GROUP BY quotation_delivery_id
HAVING n > 1
```

---
type: BigQuery Table
title: "crm_quotation_delivery"
description: "One row = one delivery round of a quotation, a record of source table `crm_quotation_delivery` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_quotation_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_quotation_delivery
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_quotation_delivery/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_quotation_delivery` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Planned delivery rounds of quotations: ship date, time window, receiver and delivery address.

Read by: [validated_derp.crm_quotation_delivery](/validated/validated_derp/crm_quotation_delivery.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_delivery_id` | STRING | UUID of the quotation delivery round. |
| `quotation_id` | STRING | UUID of the quotation in `crm_quotation`. |
| `quotation_no` | STRING | Quotation document number (e.g. `QT2607...` or `MDT2610...`). |
| `quotation_date` | STRING | Quotation document date. |
| `round_no` | INT64 | Delivery round number within the quotation (1, 2, ...). |
| `ship_date` | STRING | Planned ship date and time of the delivery round. |
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
| `created_at` | STRING | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `map_url` | STRING | Map link (e.g. Google Maps URL) of the location. |
| `nearby_landmark` | STRING | Nearby landmark of the delivery address. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_quotation_delivery/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_quotation_delivery`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_quotation_delivery`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

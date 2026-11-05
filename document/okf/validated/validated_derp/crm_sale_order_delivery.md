---
type: BigQuery Table
title: "crm_sale_order_delivery"
description: "One row = one delivery round of a sale order from source table `crm_sale_order_delivery`, unique on (sale_order_delivery_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_delivery
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_delivery.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_delivery.sqlx)"
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

Validated copy of DERP `crm_sale_order_delivery`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Delivery rounds of DERP sale orders: delivery date, time window, receiver and delivery address.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_delivery_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_delivery_id` | STRING | Unique identifier of the sale order delivery round. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `so_date` | DATETIME | Date and time of the parent sale order. |
| `round_no` | INT64 | Delivery round number within the sale order, starting at 1. |
| `delivery_date` | DATETIME | Scheduled delivery date of the delivery round. |
| `delivery_address_id` | STRING | Identifier of the customer delivery address. |
| `delivery_address_code` | STRING | Customer code of the delivery address. |
| `delivery_address_text` | STRING | Delivery address text. |
| `receiver_name` | STRING | Name of the person receiving the goods. |
| `receiver_phone` | STRING | Phone number of the person receiving the goods. |
| `remark_logistic` | STRING | Remark for logistics. |
| `order_sort` | INT64 | Display order of the delivery round within its sale order, starting at 0. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `time_start` | STRING | Start time of the delivery time window (`HH:MM:SS`). |
| `time_end` | STRING | End time of the delivery time window (`HH:MM:SS`). |
| `ship_type` | STRING | Delivery destination type (`site` or `store`). |
| `phase` | STRING | Project phase of the delivery address. |
| `house_no` | STRING | House number of the delivery address. |
| `plot` | STRING | Plot number of the delivery address. |
| `latitude` | FLOAT64 | Latitude of the delivery address. |
| `longitude` | FLOAT64 | Longitude of the delivery address. |
| `site_id` | STRING | Identifier of the shipping site (plant or warehouse). |
| `site_code` | STRING | Code of the shipping site (plant or warehouse, e.g. `KTB`, `KK1`, `LP1`). |
| `delivery_address_full` | STRING | Full delivery address. |
| `delivery_sub_district` | STRING | Sub-district of the delivery address. |
| `delivery_sub_district_code` | STRING | Sub-district code of the delivery address. |
| `delivery_district` | STRING | District of the delivery address. |
| `delivery_district_code` | STRING | District code of the delivery address. |
| `delivery_province` | STRING | Province of the delivery address. |
| `delivery_province_code` | STRING | Province code of the delivery address. |
| `delivery_postal_code` | STRING | Postal code of the delivery address. |
| `delivery_country_code` | STRING | Country code of the delivery address (e.g. `THA`). |
| `delivery_map_url` | STRING | Map URL of the delivery address. |
| `nearby_landmark` | STRING | Nearby landmark of the delivery address. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_delivery.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_delivery](/initial/raw_derp/crm_sale_order_delivery.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_delivery_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_delivery`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_delivery_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_delivery`
GROUP BY sale_order_delivery_id
HAVING n > 1
```

---
type: BigQuery Table
title: "crm_customer_address"
description: "One row = one customer address from source table `crm_customer_address`, unique on (customer_address_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_customer_address&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_customer_address
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_customer_address.sqlx"
    title: "Dataform definition (validated/derp/crm_customer_address.sqlx)"
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

Validated copy of DERP `crm_customer_address`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Business, delivery and invoice addresses of CRM customers, with Thai administrative codes and coordinates.
No other repo object reads it.

# Grain and key

One row per `customer_address_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_address_id` | STRING | UUID of the customer address record. |
| `customer_master_id` | STRING | UUID of the customer in `crm_customer_master`. |
| `customer_code` | STRING | Customer code in the CRM (e.g. `C0000136`; `NCT...` for new customers). |
| `address_type` | STRING | Address purpose (`Business`, `Delivery`, `Invoice`). |
| `address_name` | STRING | Name or label of the address. |
| `address_full` | STRING | Full address as one text string. |
| `address_detail` | STRING | Address detail line (house number, building, street). |
| `location` | STRING | Location (address) ID of the address in the ERP. |
| `sub_district` | STRING | Sub-district (tambon or khwaeng) name. |
| `sub_district_code` | STRING | Sub-district code (6-digit Thai administrative code). |
| `district` | STRING | District (amphoe or khet) name. |
| `district_code` | STRING | District code (4-digit Thai administrative code). |
| `province` | STRING | Province name. |
| `province_code` | STRING | Province code (2-digit Thai administrative code). |
| `postal_code` | STRING | Postal code. |
| `country_code` | STRING | Country code (ISO 3166 alpha-3, e.g. `THA`). |
| `latitude` | FLOAT64 | Latitude of the location in decimal degrees. |
| `longitude` | FLOAT64 | Longitude of the location in decimal degrees. |
| `delivery_note` | STRING | Delivery instructions for the address. |
| `is_primary` | BOOL | Flag marking the customer's primary address of this type. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `map_url` | STRING | Map link (e.g. Google Maps URL) of the location. |
| `is_sync` | BOOL | Flag set when the record has been synchronized with the ERP (true for migrated customers, false for records created only in the CRM). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_customer_address.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_customer_address](/initial/raw_derp/crm_customer_address.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_address_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_customer_address`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT customer_address_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_customer_address`
GROUP BY customer_address_id
HAVING n > 1
```

---
type: BigQuery Table
title: "customer_address"
description: "One row = one customer address, a record of source table `customer_address` (CIS360) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_cis360&t=customer_address&page=table"
project_id: databuffet-nonprd
dataset_id: raw_cis360
table_id: customer_address
tags: ["initial", "raw_cis360", "cis360"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/cis360/create_all_table_raw_cis360.sqlx"
    title: "Dataform definition (initial/cis360/create_all_table_raw_cis360.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/cis360/customer_address/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `customer_address` table from CIS360; nothing is cleaned or deduplicated here. Table meaning: Addresses of CIS360 customers by type (official, shipping, billing, KYC, work site, etc.) with Thai administrative areas, tax-invoice details and coordinates.

Read by: [validated_cis360.customer_address](/validated/validated_cis360/customer_address.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the address record. |
| `customer_profile_id` | STRING | Customer profile the address belongs to (`customer_profile.id`). |
| `address_type_id` | INT64 | Address type (`address_type.id`: 1 = official, 2 = shipping, 3 = contact, 4 = billing, 5 = default, 6 = KYC, 7 = work site, 8 = document delivery, 9 = warehouse). |
| `platform_id` | INT64 | Platform the address came from (1 = ALLKONS_M_BUYER, 2 = ALLKONS_M_SELLER, 4 = ALLKONS_ID, 6 = ALLKONS_AMRP, 8 = CIS360, 14 = D365). |
| `contact_name` | STRING | Name of the contact person at this address. |
| `contact_phone_number` | STRING | Whether a contact phone number is recorded for the address. |
| `contact_email` | STRING | Whether a contact email is recorded for the address. |
| `address_detail` | STRING | Additional free-text address details. |
| `address_name` | STRING | Label given to the address (e.g. site or branch name). |
| `branch` | INT64 | Tax-invoice branch number of the address. |
| `tax_invoice_juristic_type` | INT64 | Juristic entity type used on the tax invoice (`juristic_type.id`). |
| `tax_invoice_juristic_name` | STRING | Name printed on the tax invoice for this address. |
| `tax_invoice_type` | STRING | Identity document type used for the tax invoice (`ID_CARD`, `PASSPORT`, `NOT_SPECIFIED`). |
| `tax_invoice_customer_type` | INT64 | Customer type used on the tax invoice (`customer_type.id`: 1 = PERSONAL, 2 = JURISTIC). |
| `tax_invoice_tax_id` | STRING | Tax identification number printed on the tax invoice. |
| `parent` | STRING | Identifier of the parent address record this address was derived from (`customer_address.id`). |
| `address_info` | STRING | Address text line (house number, building, village). |
| `street` | STRING | Street (thanon) name of the address. |
| `country_id` | INT64 | Country of the address (`country.id`). |
| `province_id` | INT64 | Province of the address (`province.id`). |
| `district_id` | INT64 | District of the address (`district.id`). |
| `sub_district_id` | INT64 | Sub-district of the address (`sub_district.id`). |
| `zipcode_id` | INT64 | Postal code of the address (`zipcode.id`). |
| `country_name` | STRING | Country name of the address. |
| `province_name` | STRING | Province name of the address. |
| `district_name` | STRING | District name of the address. |
| `sub_district_name` | STRING | Sub-district name of the address. |
| `zipcode_name` | STRING | 5-digit postal code of the address. |
| `latitude` | STRING | Latitude of the address location. |
| `longitude` | STRING | Longitude of the address location. |
| `active_status` | BOOL | Whether the address is active. |
| `is_default` | BOOL | Whether this is the customer's default address. |
| `is_kyc_document` | BOOL | Whether the address comes from a KYC identity document. |
| `is_delete` | BOOL | Soft-delete flag (TRUE = record deleted). |
| `create_date` | STRING | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | STRING | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_cis360` (`definitions/initial/cis360/create_all_table_raw_cis360.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/cis360/customer_address/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_cis360.customer_address`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_cis360.customer_address`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

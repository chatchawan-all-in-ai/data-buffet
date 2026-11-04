---
type: BigQuery Table
title: "customer_address"
description: "One row = one customer address from source table `customer_address`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_cis360&t=customer_address&page=table"
project_id: databuffet-nonprd
dataset_id: validated_cis360
table_id: customer_address
tags: ["validated", "validated_cis360", "cis360", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/cis360/customer_address.sqlx"
    title: "Dataform definition (validated/cis360/customer_address.sqlx)"
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

Validated copy of CIS360 `customer_address`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Addresses of CIS360 customers by type (official, shipping, billing, KYC, work site, etc.) with Thai administrative areas, tax-invoice details and coordinates.
No other table or view in this repository reads it.

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the address record. |
| `customer_profile_id` | STRING | Customer profile the address belongs to (`customer_profile.id`). |
| `address_type_id` | INT64 | Address type (`address_type.id`: 1 = official, 2 = shipping, 3 = contact, 4 = billing, 5 = default, 6 = KYC, 7 = work site, 8 = document delivery, 9 = warehouse). |
| `platform_id` | INT64 | Platform the address came from (1 = ALLKONS_M_BUYER, 2 = ALLKONS_M_SELLER, 4 = ALLKONS_ID, 6 = ALLKONS_AMRP, 8 = CIS360, 14 = D365). |
| `contact_name` | STRING | Name of the contact person at this address. |
| `contact_phone_number` | BOOL | Whether a contact phone number is recorded for the address. |
| `contact_email` | BOOL | Whether a contact email is recorded for the address. |
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
| `create_date` | DATETIME | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | DATETIME | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/cis360/customer_address.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_cis360.customer_address](/initial/raw_cis360/customer_address.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_cis360.customer_address`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_cis360.customer_address`
GROUP BY id
HAVING n > 1
```

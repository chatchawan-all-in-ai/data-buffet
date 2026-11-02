---
type: BigQuery Table
title: "vendors"
description: "One row = one vendor, a record of source table `vendors` (MASTER_SKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=vendors&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: vendors
tags: ["initial", "raw_master_sku", "master_sku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx"
    title: "Dataform definition (initial/master_sku/create_all_table_raw_master_sku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/master_sku/vendors/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `vendors` table from MASTER_SKU; nothing is cleaned or deduplicated here. Table meaning: Vendors (suppliers registered via the Allkons platform) of the master_sku 3.0 product master, with registration, address and KYC status. Used by: [validated_master_sku.vendors](/validated/validated_master_sku/vendors.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the vendor. |
| `allkons_id` | STRING | Identifier of the vendor in the Allkons platform (32-character encoded ID). |
| `auth_id` | STRING | Identifier of the vendor login account. |
| `name` | STRING | Vendor (company) name. |
| `legal_entity_no` | STRING | Juristic person (company tax) registration number, 13 digits. |
| `phone_no` | STRING | Vendor phone number. |
| `country_name` | STRING | Country of the vendor address. |
| `province_name` | STRING | Province of the vendor address. |
| `district_name` | STRING | District of the vendor address. |
| `sub_district_name` | STRING | Sub-district of the vendor address. |
| `postal_code` | STRING | Postal code of the vendor address. |
| `email` | STRING | Vendor email address. |
| `address` | STRING | Street address of the vendor. |
| `company_type` | STRING | Legal entity type of the vendor (e.g. limited company, limited partnership). |
| `business_type` | STRING | Business type code of the vendor. |
| `document_id` | STRING | Identifier of the vendor registration document. |
| `is_dbd` | BOOL | Flag marking the vendor as verified with the Department of Business Development (DBD) registry. |
| `account_type` | STRING | Account type of the vendor (`Organization`). |
| `kyc_status` | STRING | KYC approval status of the vendor (`Approved`, `NotApproved`, `WaitApprove`, `NotSendApprove`, `RequestDocument`). |
| `status` | STRING | Record status (`Active`, `Inactive`, `Deleted`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/vendors/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.vendors`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_master_sku.vendors`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

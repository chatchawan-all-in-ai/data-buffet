---
type: BigQuery Table
title: "vendors"
description: "One row = one vendor from source table `vendors`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=vendors&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: vendors
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/vendors.sqlx"
    title: "Dataform definition (validated/master_sku/vendors.sqlx)"
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

Validated copy of MASTER_SKU `vendors`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Vendors (suppliers registered via the Allkons platform) of the master_sku 3.0 product master, with registration, address and KYC status.
Used by: [curated_master_sku.product_for_aisearch_v3](/curated/curated_master_sku/product_for_aisearch_v3.md).

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/master_sku/vendors.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.vendors](/initial/raw_master_sku/vendors.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.vendors`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.vendors`
GROUP BY id
HAVING n > 1
```

---
type: BigQuery Table
title: "vendor"
description: "One row = one vendor from source table `vendor`, unique on (vd_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=vendor&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: vendor
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/vendor.sqlx"
    title: "Dataform definition (validated/mastersku/vendor.sqlx)"
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

Validated copy of MASTERSKU `vendor`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Vendors (suppliers registered via the Allkons platform) of the old product master MASTERSKU, with registration, address and KYC status.

Read by: [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md).

# Grain and key

One row per `vd_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `vd_id` | STRING | Unique identifier (UUID) of the vendor. |
| `vd_api_id` | STRING | Identifier of the vendor in the Allkons platform API (32-character encoded ID). |
| `vd_code` | STRING | Vendor code. |
| `vd_name` | STRING | Vendor (company) name. |
| `vd_coporate_no` | STRING | Juristic person (company tax) registration number, 13 digits. |
| `vd_tel` | STRING | Vendor phone number. |
| `vd_country_name` | STRING | Country of the vendor address. |
| `vd_province_name` | STRING | Province of the vendor address. |
| `vd_district_name` | STRING | District of the vendor address. |
| `vd_sub_district_name` | STRING | Sub-district of the vendor address. |
| `vd_zipcode` | STRING | Postal code of the vendor address. |
| `vd_email` | STRING | Vendor email address. |
| `vd_address` | STRING | Street address of the vendor. |
| `vd_organize_name` | STRING | Legal entity type of the vendor (e.g. limited company, limited partnership). |
| `vd_business_type_name` | STRING | Business type code of the vendor. |
| `vd_document_id` | STRING | Identifier of the vendor registration document. |
| `vd_document_path` | STRING | Storage path of the vendor registration document. |
| `vd_is_dbd` | BOOL | Flag marking the vendor as verified with the Department of Business Development (DBD) registry. |
| `vd_account_type` | STRING | Account type of the vendor (`Organization`). |
| `vd_kyc_status` | STRING | KYC approval status of the vendor (`Approved`, `NotApproved`, `WaitApprove`, `NotSendApprove`, `RequestDocument`). |
| `vd_is_active` | BOOL | Active flag of the record. |
| `vd_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `vd_created_date` | DATETIME | Timestamp when the record was created. |
| `vd_updated_date` | DATETIME | Timestamp when the record was last updated. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/vendor.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.vendor](/initial/raw_mastersku/vendor.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `vd_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.vendor`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT vd_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.vendor`
GROUP BY vd_id
HAVING n > 1
```

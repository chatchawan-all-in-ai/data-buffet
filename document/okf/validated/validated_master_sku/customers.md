---
type: BigQuery Table
title: "customers"
description: "One row per `customers` from source table `customers`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=customers&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: customers
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/customers.sqlx"
    title: "Dataform definition (validated/master_sku/customers.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T21:13:49+07:00" }
status: draft
---

# What it is

Validated copy of MASTER_SKU `customers`: string values are cleaned, types are cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Customer records linked to product information.

# Grain and key

One row per (id). The key is declared in both `uniqueKey` and `pk_key`; the definition adds it as a `NOT ENFORCED` primary key after a full build.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source identifier for the record. |
| `name` | STRING | Name of the record. |
| `tax_id` | STRING | Tax identifier. |
| `phone_no` | STRING | Telephone number. |
| `address` | STRING | Postal address. |
| `country_name` | STRING | Country name. |
| `province_name` | STRING | Province name. |
| `district_name` | STRING | District name. |
| `sub_district_name` | STRING | Subdistrict name. |
| `postal_code` | STRING | Postal code. |
| `email` | STRING | Email address. |
| `document_id` | STRING | Customer document identifier. |
| `kyc_status` | STRING | Know-your-customer verification status. |
| `status` | STRING | Source status of the record. |
| `created_at` | DATETIME | UTC timestamp when the record was created. |
| `updated_at` | DATETIME | UTC timestamp when the record was last updated. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date parsed from the raw ASATDATE partition; used for deduplication and partitioning. |

# How it is built

- Definition: `definitions/validated/master_sku/customers.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.customers](/initial/raw_master_sku/customers.md).
- Incremental runs read raw partitions within the configured `BACKFILL_DAYS` window and MERGE on `uniqueKey`; the first or a full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY id ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.customers`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.customers`
GROUP BY id
HAVING n > 1
```

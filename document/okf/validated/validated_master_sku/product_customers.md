---
type: BigQuery Table
title: "product_customers"
description: "One row per `product_customers` from source table `product_customers`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=product_customers&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: product_customers
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/product_customers.sqlx"
    title: "Dataform definition (validated/master_sku/product_customers.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki: validated layer"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T22:49:49+07:00" }
status: draft
---



# What it is

Validated copy of MASTER_SKU `product_customers`: string values are cleaned, UTC datetimes are converted to Bangkok DATETIME values, the extract date is standardised to `asatdate`, and duplicate keys are collapsed. Table meaning: customer-specific product records.

# Grain and key

One row per (id). The key is declared in `uniqueKey` and `pk_key`; the definition adds it as a `NOT ENFORCED` primary key after a full build.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source record identifier. |
| `customer_id` | STRING | Customer identifier. |
| `product_id` | STRING | Product identifier; NULL when missing or whitespace-only. |
| `customer_chain` | STRING | Customer chain. |
| `product_name` | STRING | Product name supplied for the customer. |
| `product_detail` | STRING | Product detail supplied for the customer. |
| `product_status` | STRING | Product status supplied for the customer. |
| `status` | STRING | Source record status. |
| `created_at` | DATETIME | Creation datetime converted from UTC to Asia/Bangkok. |
| `created_by` | STRING | Creator identifier. |
| `updated_at` | DATETIME | Update datetime converted from UTC to Asia/Bangkok. |
| `updated_by` | STRING | Updater identifier. |
| `asatdate` | DATE | Extract date parsed from the raw ASATDATE partition. |

# How it is built

- Definition: `definitions/validated/master_sku/product_customers.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.product_customers](../../initial/raw_master_sku/product_customers.md).
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY id ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by id.

# Examples

Recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.product_customers`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

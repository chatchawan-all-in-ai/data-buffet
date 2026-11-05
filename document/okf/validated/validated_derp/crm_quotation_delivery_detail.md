---
type: BigQuery Table
title: "crm_quotation_delivery_detail"
description: "One row = one product line of a quotation delivery round from source table `crm_quotation_delivery_detail`, unique on (quotation_delivery_detail_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_quotation_delivery_detail&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_quotation_delivery_detail
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_quotation_delivery_detail.sqlx"
    title: "Dataform definition (validated/derp/crm_quotation_delivery_detail.sqlx)"
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

Validated copy of DERP `crm_quotation_delivery_detail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Products and quantities to deliver in each quotation delivery round.
No other table or view in this repository reads it.

# Grain and key

One row per `quotation_delivery_detail_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_delivery_detail_id` | STRING | UUID of the delivery round line. |
| `quotation_delivery_id` | STRING | UUID of the delivery round in `crm_quotation_delivery`. |
| `quotation_id` | STRING | UUID of the quotation in `crm_quotation`. |
| `quotation_no` | STRING | Quotation document number (e.g. `QT2607...` or `MDT2610...`). |
| `quotation_date` | DATE | Quotation document date. |
| `product_id` | STRING | UUID of the product in the DERP product master. |
| `product_code` | STRING | Product (item) code. |
| `product_name` | STRING | Product name. |
| `qty_delivered` | INT64 | Quantity of the product to deliver in the round. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `order_sort` | INT64 | Display order of the row within its parent record. |
| `combo_set_id` | STRING | UUID of the combo set (product bundle) the line belongs to. |
| `combo_set_code` | STRING | Code of the combo set (product bundle) the line belongs to (e.g. `COMBOSET00014`). |
| `quotation_detail_id` | STRING | UUID of the quotation line in `crm_quotation_detail`. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_quotation_delivery_detail.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_quotation_delivery_detail](/initial/raw_derp/crm_quotation_delivery_detail.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `quotation_delivery_detail_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_quotation_delivery_detail`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT quotation_delivery_detail_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_quotation_delivery_detail`
GROUP BY quotation_delivery_detail_id
HAVING n > 1
```

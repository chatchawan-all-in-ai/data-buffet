---
type: BigQuery Table
title: "crm_sale_order_attachment"
description: "One row = one file attached to a sale order from source table `crm_sale_order_attachment`, unique on (sale_order_attachment_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_attachment&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_attachment
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_attachment.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_attachment.sqlx)"
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

Validated copy of DERP `crm_sale_order_attachment`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Files attached to DERP sale orders (customer POs, maps, pay-in evidence).
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_attachment_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_attachment_id` | STRING | Unique identifier of the sale order attachment. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `attachment_type` | STRING | Type of the attached document (e.g. `PO`, `MAP`, `Payin`, `Other`). |
| `attach_source` | STRING | Who attached the file (`Admin` or `TA`). |
| `file_id` | STRING | Identifier of the stored file. |
| `file_name` | STRING | File name of the attachment. |
| `file_url` | STRING | URL of the attachment. |
| `file_size` | INT64 | File size in bytes. |
| `mime_type` | STRING | MIME type of the file (e.g. `application/pdf`, `image/png`). |
| `po_ref` | STRING | Customer purchase order (PO) number of the attached PO. |
| `expiry_date` | DATE | Expiry date of the attached document (e.g. PO expiry). |
| `note` | STRING | Free-text note on the attachment. |
| `order_sort` | INT64 | Display order of the attachment within its sale order. |
| `amount` | FLOAT64 | Amount stated on the attached document (THB). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_attachment.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_attachment](/initial/raw_derp/crm_sale_order_attachment.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_attachment_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_attachment`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_attachment_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_attachment`
GROUP BY sale_order_attachment_id
HAVING n > 1
```

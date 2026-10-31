---
type: BigQuery Table
title: "crm_quotation_detail"
description: "One row = one cleaned copy of the source table `crm_quotation_detail`, unique on (quotation_detail_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_quotation_detail&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_quotation_detail
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_quotation_detail.sqlx"
    title: "Dataform definition (validated/derp/crm_quotation_detail.sqlx)"
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

Validated copy of DERP `crm_quotation_detail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `quotation_detail_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_detail_id` | STRING | Meaning not documented in the repo. |
| `quotation_id` | STRING | Meaning not documented in the repo. |
| `quotation_date` | DATE | Meaning not documented in the repo. |
| `quotation_no` | STRING | Meaning not documented in the repo. |
| `product_id` | STRING | Meaning not documented in the repo. |
| `product_code` | STRING | Meaning not documented in the repo. |
| `promo_price` | FLOAT64 | Meaning not documented in the repo. |
| `unit_price` | FLOAT64 | Meaning not documented in the repo. |
| `unit` | STRING | Meaning not documented in the repo. |
| `offer_unit_price` | FLOAT64 | Meaning not documented in the repo. |
| `offer_promo_price` | FLOAT64 | Meaning not documented in the repo. |
| `distribution_percent` | FLOAT64 | Meaning not documented in the repo. |
| `free_type` | BOOL | Meaning not documented in the repo. |
| `list_price` | FLOAT64 | Meaning not documented in the repo. |
| `normal_disc` | FLOAT64 | Meaning not documented in the repo. |
| `special_disc_1` | FLOAT64 | Meaning not documented in the repo. |
| `special_disc_2` | FLOAT64 | Meaning not documented in the repo. |
| `special_disc_3` | FLOAT64 | Meaning not documented in the repo. |
| `percent_disc` | FLOAT64 | Meaning not documented in the repo. |
| `qty_total` | INT64 | Meaning not documented in the repo. |
| `total_amount` | FLOAT64 | Meaning not documented in the repo. |
| `distribution_amount` | FLOAT64 | Meaning not documented in the repo. |
| `sale_type` | STRING | Meaning not documented in the repo. |
| `order_sort` | INT64 | Meaning not documented in the repo. |
| `project_product_id` | STRING | Meaning not documented in the repo. |
| `project_product_code` | STRING | Meaning not documented in the repo. |
| `project_promo_price` | FLOAT64 | Meaning not documented in the repo. |
| `project_unit_price` | FLOAT64 | Meaning not documented in the repo. |
| `project_unit` | STRING | Meaning not documented in the repo. |
| `project_offer_unit_price` | FLOAT64 | Meaning not documented in the repo. |
| `project_offer_promo_price` | FLOAT64 | Meaning not documented in the repo. |
| `project_distribution_percent` | FLOAT64 | Meaning not documented in the repo. |
| `project_free_type` | BOOL | Meaning not documented in the repo. |
| `project_list_price` | FLOAT64 | Meaning not documented in the repo. |
| `project_normal_disc` | FLOAT64 | Meaning not documented in the repo. |
| `project_special_disc_1` | FLOAT64 | Meaning not documented in the repo. |
| `project_special_disc_2` | FLOAT64 | Meaning not documented in the repo. |
| `project_special_disc_3` | FLOAT64 | Meaning not documented in the repo. |
| `project_percent_disc` | FLOAT64 | Meaning not documented in the repo. |
| `project_qty_total` | INT64 | Meaning not documented in the repo. |
| `project_total_amount` | FLOAT64 | Meaning not documented in the repo. |
| `project_distribution_amount` | FLOAT64 | Meaning not documented in the repo. |
| `project_sale_type` | STRING | Meaning not documented in the repo. |
| `project_order_sort` | INT64 | Meaning not documented in the repo. |
| `mac5_id` | INT64 | Meaning not documented in the repo. |
| `mac5_detail_id` | INT64 | Meaning not documented in the repo. |
| `mac5_code` | STRING | Meaning not documented in the repo. |
| `revamp_id` | INT64 | Meaning not documented in the repo. |
| `revamp_detail_id` | INT64 | Meaning not documented in the repo. |
| `revamp_code` | STRING | Meaning not documented in the repo. |
| `d365_id` | INT64 | Meaning not documented in the repo. |
| `d365_detail_id` | INT64 | Meaning not documented in the repo. |
| `d365_code` | STRING | Meaning not documented in the repo. |
| `ref_1_id` | INT64 | Meaning not documented in the repo. |
| `ref_1_detail_id` | INT64 | Meaning not documented in the repo. |
| `ref_1_code` | STRING | Meaning not documented in the repo. |
| `ref_2_id` | INT64 | Meaning not documented in the repo. |
| `ref_2_detail_id` | INT64 | Meaning not documented in the repo. |
| `ref_2_code` | STRING | Meaning not documented in the repo. |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `updated_by_name` | STRING | Meaning not documented in the repo. |
| `combo_set_id` | STRING | Meaning not documented in the repo. |
| `combo_set_code` | STRING | Meaning not documented in the repo. |
| `project_combo_set_id` | STRING | Meaning not documented in the repo. |
| `project_combo_set_code` | STRING | Meaning not documented in the repo. |
| `bu_code` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `bu_name` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `project_bu_code` | STRING | Meaning not documented in the repo. |
| `project_bu_name` | STRING | Meaning not documented in the repo. |
| `bu_id` | STRING | Meaning not documented in the repo. |
| `project_bu_id` | STRING | Meaning not documented in the repo. |
| `sales_id` | STRING | Meaning not documented in the repo. |
| `sales_code` | STRING | Meaning not documented in the repo. |
| `sales_name` | STRING | Meaning not documented in the repo. |
| `parent_quotation_detail_id` | STRING | Meaning not documented in the repo. |
| `lv` | INT64 | Meaning not documented in the repo. |
| `project_mac5_code` | STRING | Meaning not documented in the repo. |
| `distribution_amount_per_unit` | FLOAT64 | Meaning not documented in the repo. |
| `qty_remaining` | INT64 | Meaning not documented in the repo. |
| `qty_used` | INT64 | Meaning not documented in the repo. |
| `product_description` | STRING | Meaning not documented in the repo. |
| `freebie_main_detail_id` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_quotation_detail.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_quotation_detail](/initial/raw_derp/crm_quotation_detail.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `quotation_detail_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 14,794 rows, 8.5 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_quotation_detail`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT quotation_detail_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_quotation_detail`
GROUP BY quotation_detail_id
HAVING n > 1
```

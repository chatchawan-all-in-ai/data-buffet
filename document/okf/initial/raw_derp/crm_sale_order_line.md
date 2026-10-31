---
type: BigQuery Table
title: "crm_sale_order_line"
description: "One row = one record of source table `crm_sale_order_line` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_sale_order_line&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_sale_order_line
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_sale_order_line/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_sale_order_line` table from DERP; nothing is cleaned or deduplicated here. Used by: [validated_derp.crm_sale_order_line](/validated/validated_derp/crm_sale_order_line.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_line_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_order_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `so_date` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `quotation_detail_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unit` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `list_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `unit_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `promo_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `offer_unit_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `offer_promo_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `normal_disc` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `special_disc_1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `special_disc_2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `special_disc_3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `percent_disc` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `distribution_percent` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `distribution_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `free_type` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `qty_total` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_rate` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sale_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `order_sort` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_detail_id` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mac5_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_at` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `created_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `updated_by_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `site_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `site_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `vat_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `grand_total_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bu_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bu_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sales_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `delivered_qty` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `remaining_qty` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `combo_set_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `combo_set_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `distribution_amount_per_unit` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `promotion_qty_per_set` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_description` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `product_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `master_unit_price` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `price_override_reason` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `asset_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `line_item_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `requires_delivery` | BOOL | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `cost_group_id` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `line_discount_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `trade_discount_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `net_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `base_amount` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `stock_grade` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_sale_order_line/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_sale_order_line`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_sale_order_line`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

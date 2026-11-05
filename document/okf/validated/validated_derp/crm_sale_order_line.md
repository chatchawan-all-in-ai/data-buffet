---
type: BigQuery Table
title: "crm_sale_order_line"
description: "One row = one sale order line from source table `crm_sale_order_line`, unique on (sale_order_line_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_line&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_line
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_line.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_line.sqlx)"
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

Validated copy of DERP `crm_sale_order_line`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product lines of DERP sale orders with quantities, prices, discounts and amounts.
No other repo object reads it.

# Grain and key

One row per `sale_order_line_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_line_id` | STRING | Unique identifier of the sale order line. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `so_date` | DATETIME | Date and time of the parent sale order. |
| `quotation_detail_id` | STRING | Identifier of the source quotation line (`crm_quotation_detail`). |
| `product_id` | STRING | Identifier of the product. |
| `product_code` | STRING | Product code (SKU, e.g. `OWT_GNT`). |
| `unit` | STRING | Sales unit of the product (e.g. `EA`, `SET`, or a Thai unit name). |
| `list_price` | FLOAT64 | List price per unit (THB). |
| `unit_price` | FLOAT64 | Selling price per unit before VAT (THB). |
| `promo_price` | FLOAT64 | Promotion price per unit (THB). |
| `offer_unit_price` | FLOAT64 | Offered price per unit (THB). |
| `offer_promo_price` | FLOAT64 | Offered promotion price per unit (THB). |
| `normal_disc` | FLOAT64 | Normal discount in percent. |
| `special_disc_1` | FLOAT64 | First special discount in percent. |
| `special_disc_2` | FLOAT64 | Second special discount in percent. |
| `special_disc_3` | FLOAT64 | Third special discount in percent. |
| `percent_disc` | FLOAT64 | Total discount in percent. |
| `distribution_percent` | FLOAT64 | Distribution fee in percent. |
| `distribution_amount` | FLOAT64 | Distribution fee amount for the line (THB). |
| `free_type` | BOOL | TRUE when the line is a free item. |
| `qty_total` | INT64 | Ordered quantity. |
| `total_amount` | FLOAT64 | Line amount before VAT (THB). |
| `vat_rate` | FLOAT64 | VAT rate of the line in percent (e.g. `7`). |
| `sale_type` | STRING | Sale type of the line (e.g. general goods, `combo`, `promo`). |
| `order_sort` | INT64 | Display order of the row within its sale order, starting at 0. |
| `mac5_id` | INT64 | Identifier of the matching document in the MAC5 ERP. |
| `mac5_detail_id` | INT64 | Identifier of the matching document line in the MAC5 ERP. |
| `mac5_code` | STRING | Document code of the matching document in the MAC5 ERP. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `site_id` | STRING | Identifier of the shipping site (plant or warehouse). |
| `site_code` | STRING | Code of the shipping site (plant or warehouse, e.g. `KTB`, `KK1`, `LP1`). |
| `vat_amount` | FLOAT64 | VAT amount of the line (THB). |
| `grand_total_amount` | FLOAT64 | Line total including VAT (THB). |
| `bu_id` | STRING | Identifier of the business unit of the product. |
| `bu_code` | STRING | Business unit code of the product (e.g. `01`, `LT`). |
| `sales_id` | STRING | Identifier of the salesperson. |
| `sales_code` | STRING | Employee code of the salesperson. |
| `sales_name` | STRING | Name of the salesperson. |
| `delivered_qty` | FLOAT64 | Quantity already delivered. |
| `remaining_qty` | FLOAT64 | Quantity still to be delivered. |
| `combo_set_id` | STRING | Identifier of the combo set (product bundle) the line belongs to. |
| `combo_set_code` | STRING | Code of the combo set (product bundle) the line belongs to (e.g. `COMBOSET00006`). |
| `distribution_amount_per_unit` | FLOAT64 | Distribution fee amount per unit (THB). |
| `promotion_qty_per_set` | FLOAT64 | Quantity of the product per promotion set. |
| `product_description` | STRING | Product description. |
| `product_name` | STRING | Product name. |
| `master_unit_price` | FLOAT64 | Unit price from the price master (THB). |
| `price_override_reason` | STRING | Reason the unit price was overridden. |
| `asset_id` | STRING | Identifier of the asset linked to the line. |
| `line_item_type` | STRING | Line item type (`GOODS` or `SERVICE`). |
| `requires_delivery` | BOOL | TRUE when the line requires physical delivery. |
| `cost_group_id` | STRING | Identifier of the cost group of the line. |
| `line_discount_amount` | FLOAT64 | Discount amount of the line (THB). |
| `trade_discount_amount` | FLOAT64 | Trade discount amount allocated to the line (THB). |
| `net_amount` | FLOAT64 | Net line amount after discounts (THB). |
| `base_amount` | FLOAT64 | Base line amount used for the discount calculation (THB). |
| `stock_grade` | STRING | Stock grade of the product (e.g. `A`). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_line.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_line](/initial/raw_derp/crm_sale_order_line.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_line_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_line`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_line_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_line`
GROUP BY sale_order_line_id
HAVING n > 1
```

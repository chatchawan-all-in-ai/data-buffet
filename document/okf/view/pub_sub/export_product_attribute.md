---
type: BigQuery View
title: "export_product_attribute"
description: "One row = one product attribute row, exposed for the Pub/Sub export of the AI team sample table onetime.Product_Attribute with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_product_attribute&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_product_attribute
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_product_attribute.sqlx"
    title: "Dataform definition (view/pub_sub/export_product_attribute.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `product_attribute` to topic `export-ta-product_attribute`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one product attribute row: key `ProductSK` plus `occurrence` (the position of the row among rows with the same key, ordered by their data JSON); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductSK` | INT64 | SK of a matching `dim_product_master` row (stable MERGE dim). Matching uses company + `ProductCode`, without barcode; several retained barcode versions can produce different SKs for one code. |
| `ProductCode` | STRING | Product (stock item) code. |
| `ProductSeries` | STRING | Product series name. |
| `ProductSize` | STRING | Size of the product. |
| `ProductUnit` | STRING | Sales unit of the product (e.g. `EA`). |
| `ProductModel` | STRING | Product model. |
| `ProductMaterials` | STRING | Main material of the product (e.g. PE). |
| `ProductColor` | STRING | Color of the product. |
| `ProductShape` | STRING | Packaging shape of the product (e.g. box, gallon, length). |
| `ProductGrossWeight` | FLOAT64 | Gross (packed) weight of the product. |
| `ProductNetWeight` | FLOAT64 | Net weight of the product. |
| `ProductSizeHight` | FLOAT64 | Product height. |
| `ProductSizeLong` | FLOAT64 | Product length (depth). |
| `ProductSizeWide` | FLOAT64 | Product width. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_product_attribute.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [onetime.Product_Attribute](/view/onetime/Product_Attribute.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `onetime.Product_Attribute`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_product_attribute`
GROUP BY row_key
HAVING n > 1
```

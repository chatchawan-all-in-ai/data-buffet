# curated_master_sku

2 cards in BigQuery dataset `curated_master_sku`.

# Tables

* [curated_products](curated_products.md) - One row = one product (master SKU) of the master_sku 3.0 catalogue, in the same 50-column layout as the old curated_product.
* [product_for_aisearch_v3](product_for_aisearch_v3.md) - One row = one product (master SKU) per run date, in the shape the AI search index reads: an id plus a structData struct.

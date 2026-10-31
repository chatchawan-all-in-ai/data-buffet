# curated_mastersku

2 cards in BigQuery dataset `curated_mastersku`.

# Tables

* [curated_product](curated_product.md) - One row = one product SKU of the legacy MASTERSKU catalogue, unique on prdSku (latest prdUpdatedDate wins).
* [product_for_aisearch](product_for_aisearch.md) - One row = one product SKU per run date, in the shape the AI search index reads: an id plus a structData struct (legacy MASTERSKU source).

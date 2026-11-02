# validated_mastersku

11 cards in BigQuery dataset `validated_mastersku`.

# Tables

* [brand](brand.md) - One row = one brand from source table `brand`, unique on (bra_id).
* [category](category.md) - One row = one product category from source table `category`, unique on (cat_id).
* [product](product.md) - One row = one product (SKU) from source table `product`, unique on (prd_id).
* [product_admin_status](product_admin_status.md) - One row = one admin review status from source table `product_admin_status`, unique on (pas_id).
* [product_category](product_category.md) - One row = one product-to-category link from source table `product_category`, unique on (pc_id).
* [product_detail](product_detail.md) - One row = one product detail record from source table `product_detail`, unique on (pd_id).
* [product_group](product_group.md) - One row = one product group from source table `product_group`, unique on (pg_id).
* [product_group_cost_group](product_group_cost_group.md) - One row = one product group cost-group assignment from source table `product_group_cost_group`, unique on (pgcg_id).
* [product_status](product_status.md) - One row = one product status from source table `product_status`, unique on (ps_id).
* [unit](unit.md) - One row = one measurement unit from source table `unit`, unique on (unit_id).
* [vendor](vendor.md) - One row = one vendor from source table `vendor`, unique on (vd_id).

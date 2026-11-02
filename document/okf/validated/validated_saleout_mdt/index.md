# validated_saleout_mdt

12 cards in BigQuery dataset `validated_saleout_mdt`.

# Tables

* [detail_sales_daily](detail_sales_daily.md) - One row = one article, branch and sales channel on one sale date from source table `detail_sales_daily`, unique on (sale_date, branch, article_id, distribution_channel).
* [report_sale_subscription](report_sale_subscription.md) - One row = one SKU at one Thai Watsadu branch in one daily file from source table `report_sale_subscription` (no declared key; append-style, not deduplicated).
* [sale_by_branch_detail](sale_by_branch_detail.md) - One row = one article, branch and sales channel for one report date from source table `sale_by_branch_detail`, unique on (branch, article_id, distribution_channel, end_date).
* [sale_by_branch_mch3](sale_by_branch_mch3.md) - One row = one branch and merchandise category for one report date from source table `sale_by_branch_mch3`, unique on (vendor_id, branch, mch3).
* [saleout_dh](saleout_dh.md) - One row = one product, branch, sale date and sale/return flag from source table `saleout_dh`, unique on (sale_date, branch_code, product_code, is_return).
* [saleout_gb](saleout_gb.md) - One row = one product line of one Global House bill from source table `saleout_gb`, unique on (sale_no, sale_date, branch_code, product_code).
* [saleout_hp](saleout_hp.md) - One row = one article, branch and sale date from source table `saleout_hp`, unique on (siteno, artno, sale_date).
* [sales_by_branch](sales_by_branch.md) - One row = one Boonthavorn branch for one report date from source table `sales_by_branch`, unique on (vendor_id, branch).
* [stock_aging](stock_aging.md) - One row per (vendor_id, branch, article_id, aging_tier, brand, mch3, mch2, end_date, asatdate) after SQL deduplication; fully rebuilt, with arbitrary selection among tied source records.
* [stock_by_branch](stock_by_branch.md) - One row per (vendor_id, branch, article_id, end_date, asatdate) after SQL deduplication; fully rebuilt, with arbitrary selection among tied source records.
* [turnover](turnover.md) - One row = one branch and merchandise category on one snapshot date from source table `turnover`, unique on (vendor_id, branch, mch3).
* [turnover_brand](turnover_brand.md) - One row = one merchandise category, brand and stock class on one snapshot date from source table `turnover_brand`, unique on (vendor_id, mch3, brand, class_stock).

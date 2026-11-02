# raw_saleout_mdt

19 cards in BigQuery dataset `raw_saleout_mdt`.

# Tables

* [detail_sales_daily](detail_sales_daily.md) - One row = one article, branch and sales channel on one sale date, a record of source table `detail_sales_daily` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [eom_bt_sale_by_branch_detail](eom_bt_sale_by_branch_detail.md) - One row = one article, branch and sales channel in one month-end report, a record of source table `eom_bt_sale_by_branch_detail` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [eom_bt_sales_by_branch](eom_bt_sales_by_branch.md) - One row = one Boonthavorn branch in one month-end report, a record of source table `eom_bt_sales_by_branch` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [eom_gb](eom_gb.md) - One row = one product line of one Global House bill in a month-end report, a record of source table `eom_gb` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [eom_hp](eom_hp.md) - One row = one article and branch in one monthly report version, a record of source table `eom_hp` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [eom_tw](eom_tw.md) - One row = one SKU at one Thai Watsadu branch in one month-end report, a record of source table `eom_tw` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [report_sale_subscription](report_sale_subscription.md) - One row = one SKU at one Thai Watsadu branch in one daily file, a record of source table `report_sale_subscription` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [sale_by_branch_detail](sale_by_branch_detail.md) - One row = one article, branch and sales channel for one report date, a record of source table `sale_by_branch_detail` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [sale_by_branch_mch3](sale_by_branch_mch3.md) - One row = one branch and merchandise category for one report date, a record of source table `sale_by_branch_mch3` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [saleout_dh](saleout_dh.md) - One row = one product, branch, sale date and sale/return flag, a record of source table `saleout_dh` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [saleout_gb](saleout_gb.md) - One row = one product line of one Global House bill, a record of source table `saleout_gb` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [saleout_hp](saleout_hp.md) - One row = one article, branch and sale date, a record of source table `saleout_hp` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [saleout_lastyear](saleout_lastyear.md) - One row = one product, branch and sale date, a record of source table `saleout_lastyear` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [saleout_lastyear_monthly](saleout_lastyear_monthly.md) - One row = one product, branch and month, a record of source table `saleout_lastyear_monthly` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [sales_by_branch](sales_by_branch.md) - One row = one Boonthavorn branch for one report date, a record of source table `sales_by_branch` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [stock_aging](stock_aging.md) - One row = one article age band at one Boonthavorn branch on one snapshot date, a record of source table `stock_aging` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [stock_by_branch](stock_by_branch.md) - One row = one article stock snapshot at one Boonthavorn branch, a record of source table `stock_by_branch` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [turnover](turnover.md) - One row = one branch and merchandise category on one snapshot date, a record of source table `turnover` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).
* [turnover_brand](turnover_brand.md) - One row = one merchandise category, brand and stock class on one snapshot date, a record of source table `turnover_brand` (SALEOUT_MDT) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned).

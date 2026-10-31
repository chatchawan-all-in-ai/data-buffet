# fact_view

11 cards in BigQuery dataset `fact_view`.

# Tables

* [view_aging_ri](view_aging_ri.md) - One row = one not-yet-fully-collected invoice, credit note or debit note per company (AR aging) with due dates, outstanding amount, aging days and receipt history text.
* [view_fact_mir_rs](view_fact_mir_rs.md) - One row = one receipt (mirtype RS) line or cheque of fact_mir_rs, extended with AgingSK and the receipt document's cancel flag and status name; ReceiveSK is unique.
* [view_fact_mir_vs](view_fact_mir_vs.md) - One row = one billing (mirtype VS) line of fact_mir_vs per company, extended with the AgingSK of the invoice it bills; BillingSK is unique.
* [view_fact_salein_director_mdt](view_fact_salein_director_mdt.md) - One row = one day x product x marketing group x report line x region/manager/director combination of sell-in sales to the director with DirectorID 00004, aggregated from view_fact_transcation.
* [view_fact_salein_mdt](view_fact_salein_mdt.md) - One row = one sales document line of fact_transcation sold to a modern-trade chain customer (MH, HP, TW, GB, DH, BT), tagged with chain code and the matching MDT branch/zone SK.
* [view_fact_saleout_pc_mdt](view_fact_saleout_pc_mdt.md) - One row = one fact_saleout_monthly_mdt sell-out row split evenly across the PCs assigned to its branch and marketing group in that month.
* [view_fact_stock_nonmove_mdt](view_fact_stock_nonmove_mdt.md) - One row = the latest in-stock snapshot (onhand_qty > 0) of one product at one chain branch, with its last sale date and a slow/non-moving status bucket.
* [view_fact_target_pc_mdt](view_fact_target_pc_mdt.md) - One row = one fact_target_saleout_mdt target row (day x branch x marketing group/segment) split evenly across the PCs assigned to the branch and marketing group in that month.
* [view_fact_target_product_group_mdt](view_fact_target_product_group_mdt.md) - One row = one day x marketing product group x report line x region/manager/director combination of the MDT-channel sales target, aggregated from dim_target_product_group_by_sale_dayofwork.
* [view_fact_target_section_mdt](view_fact_target_section_mdt.md) - One row = one day x modern-trade chain x marketing group, with the summed sell-out target amount and the number of branches with a target.
* [view_fact_transcation](view_fact_transcation.md) - One row = one sales document line (IS/AS/BS/QS) per company with all org, product, customer, channel and flag SKs, plus one zero-valued row per company and date without any line.

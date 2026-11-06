# dimension_view

18 cards in BigQuery dataset `dimension_view`.

# Tables

* [view_dim_aging](view_dim_aging.md) - One row = one invoice (AgingSK) in the current accounts-receivable aging, with its channel, aging bucket and receipt-age measures.
* [view_dim_aging_history](view_dim_aging_history.md) - One row = one AR document in a non-completed group under a prior-day asatdate label, with SKs re-derived from natural keys.
* [view_dim_calendar](view_dim_calendar.md) - One row = one calendar date, with day/week/month/quarter attributes, holiday flags and the LatestDateFilter flag.
* [view_dim_channel](view_dim_channel.md) - One row = one MAC5 department code (DepCode) of a company, with its sales, finance and cost channel mappings and their SKs.
* [view_dim_company](view_dim_company.md) - One row = one company (CompanySK) with report-friendly company names and a merged report company code.
* [view_dim_customer](view_dim_customer.md) - One row = one customer with each matching nickname and key-account record, with group SK and address names; CustomerSK can repeat.
* [view_dim_customer_credit_management](view_dim_customer_credit_management.md) - One row = one customer (CustomerSK) with credit terms/limit and its latest invoice and due credit-management grades.
* [view_dim_customer_report_info](view_dim_customer_report_info.md) - One row = one report shop name (CustomerReportName) per company, with its segment, PC flag, online info, responsible sales chain (TA) and address names.
* [view_dim_guarantee](view_dim_guarantee.md) - One row = one bank guarantee (GuaranteeSK) per company, customer and bank, linked to its CustomerSK.
* [view_dim_invoice](view_dim_invoice.md) - One row = one `dim_invoice` sales document with each matching customer and name record, with order/aging SKs, SCG flag and a resolved shop name; `InvoiceSK` can repeat.
* [view_dim_order](view_dim_order.md) - One row = one sales order (OrderSK, MAC5 PS document) with status, order type, ship-to and an expiry flag.
* [view_dim_product_master](view_dim_product_master.md) - One row = one product (`ProductSK`) from dim_product_master with rebate exclusion flags (`FlagSalesExc`, `FlagAccExc`) and the pump segment (`PumpSegment`).
* [view_dim_product_mkt](view_dim_product_mkt.md) - One row = one product marketing classification with each matching director record, or NULL when unmatched; ProductMktSK repeats when several director records match.
* [view_dim_sale_representative](view_dim_sale_representative.md) - One row = one sales representative assignment with each distinct matching department name; SaleRepSK can repeat across department names.
* [view_dim_sale_representative_last](view_dim_sale_representative_last.md) - One row = one sales-representative rule or ledger row (`SaleRepSK`) in the latest organisation; an employee can have several rows.
* [view_dim_target_by_agent](view_dim_target_by_agent.md) - One row = one sales target (product group, year, month, target ID) allocated to one salesperson, with the latest org-chart SKs.
* [view_dim_target_by_agent_dayofwork](view_dim_target_by_agent_dayofwork.md) - One row = one allocated sales target spread to one calendar date (working days only get a share), with the as-of-date org SKs.
* [view_sales_representative_last](view_sales_representative_last.md) - One row = one sales-representative assignment rule in the latest organisation, with department, section and region IDs and names resolved; an employee can have several rows.

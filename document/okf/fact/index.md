# Fact

Star-schema facts in `fact_table` plus the AR chain.

# Tables

* [fact_backlog_store](fact_backlog_store.md) - One row = one product (cpsStkID) on one open sales order (cpsVnosID) per customer and store, with requested and cut quantities from the latest cps snapshot.
* [fact_chq](fact_chq.md) - One row = one cheque (chqno) per customer per company, linked to the receipt line (cqlvnos) that records it, for cheques with cqlbook = 0.
* [fact_delivery](fact_delivery.md) - Delivery status groups enriched with invoice/product candidates; retained product versions can repeat both invoice measures and delivery status counts.
* [fact_invoice](fact_invoice.md) - One row = one product (milStk) on one invoice-type document (IS/BS/AS/QS) per customer and link number per company, within the last 4 years.
* [fact_invoice_store](fact_invoice_store.md) - One row = one product line of an invoice (IS) per salesperson share (milPer) for ag01/ab01, with invoice, order, product, customer and store SKs.
* [fact_mir_rs](fact_mir_rs.md) - One row = one receipt (RS) document line against an invoice, optionally matched to the billing row (BillingSK) and to the cheque (FactChqSK) that paid it, or a cheque with no receipt line.
* [fact_mir_vs](fact_mir_vs.md) - One row = one billing (VS) document line of a company that bills an invoice (mirbinvno), de-duplicated to one row per invoice.
* [fact_order](fact_order.md) - PS order aggregates expanded by retained product versions and matching quotation rows; quantities and amounts can repeat within a company/order/product.
* [fact_order_store](fact_order_store.md) - One row = one product line (milListNo) of a sales order (PS) in a warehouse-flagged status for ag01/ab01, with product, customer and store SKs.
* [fact_quotation](fact_quotation.md) - Quotation detail aggregates by quotation, customer, project, company and matched ProductSK; retained barcode versions can repeat quoted quantities and totals.
* [fact_saleout_mdt](fact_saleout_mdt.md) - One row = one sell-out (sale or return) document-type total per sale date, store (chain), branch and product from the modern-trade chains' daily feeds.
* [fact_saleout_monthly_mdt](fact_saleout_monthly_mdt.md) - One row = one chain (store_code) x branch x sales channel x product x month_date total of sell-out as reported by the chain monthly (or collapsed from the daily feed).
* [fact_stock_mdt](fact_stock_mdt.md) - One row = on-hand (and on-order) stock of one product at one chain branch on one stock date.
* [fact_stock_mdt_monthly](fact_stock_mdt_monthly.md) - One row = the stock position of one product at one chain branch on the last usable stock date of a month for that chain.
* [fact_target_saleout_mdt](fact_target_saleout_mdt.md) - One row = the daily sell-out target of one MDT branch for one marketing group / sub-marketing / segment on one date.
* [fact_target_series_mdt](fact_target_series_mdt.md) - One row = the daily target quantity of one MDT branch for one product series on one date.
* [fact_transaction_delivery](fact_transaction_delivery.md) - IS invoice aggregates by customer, company, InvoiceSK and matched ProductSK; retained barcode versions can repeat invoiced measures.
* [fact_transcation](fact_transcation.md) - One row = one bill line (IS/AS/BS/QS document line, milListno) per company, enriched with product, customer, channel, sales-organisation and marketing SKs, for the last four years.

# onetime

5 cards in BigQuery dataset `onetime`.

# Tables

* [Model_Invoice_Transaction](Model_Invoice_Transaction.md) - One row = one view_fact_transcation line of CompanySK 4 for 2024-2026 with IDs and names; a line repeats once per matching dim_product_master row.
* [Model_Target_DayOfWork](Model_Target_DayOfWork.md) - One row = one day-of-work target for CompanySK 4, with org (latest structure), marketing and report names.
* [Product_Attribute](Product_Attribute.md) - One row = one combination of a barcoded MAC5 stock item, matching dim_product_master rows and MASTERSKU attribute rows.
* [Product_Master_ALL](Product_Master_ALL.md)
* [Transaction_Data_Mart](Transaction_Data_Mart.md) - One row = one line (curated_mil) of an invoice, debit note, credit note or QS document (types IS/AS/BS/QS) per company, with header fields, VAT allocation and address SKs.

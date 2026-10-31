# onetime

5 cards in BigQuery dataset `onetime`.

# Tables

* [Model_Invoice_Transaction](Model_Invoice_Transaction.md) - Sales rows of CompanySK 4 for 2024-2026 enriched with names; retained product barcode versions can repeat each source row and its measures.
* [Model_Target_DayOfWork](Model_Target_DayOfWork.md) - One row = one day-of-work target for CompanySK 4, with marketing/report names and potentially incorrect org attributes due to joins across independently numbered dimension families.
* [Product_Attribute](Product_Attribute.md) - Current barcoded ag01 MAC5 stock joined to matching dim_product_master ProductSK rows and MASTERSKU attributes; a code can have multiple retained barcode versions.
* [Product_Master_ALL](Product_Master_ALL.md) - An ag01 dim_product_master barcode version enriched with descriptions, marketing hierarchy, marketing director and physical attributes; enrichment joins can multiply rows.
* [Transaction_Data_Mart](Transaction_Data_Mart.md) - One row = one line (curated_mil) of an invoice, debit note, credit note or QS document (types IS/AS/BS/QS) per company, with header fields, VAT allocation and address SKs.

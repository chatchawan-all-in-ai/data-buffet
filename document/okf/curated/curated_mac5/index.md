# curated_mac5

3 cards in BigQuery dataset `curated_mac5`.

# Tables

* [curated_mih](curated_mih.md) - One row = one MAC5 document header (order, invoice, billing, etc.) per company, unique on (company_id, mihType, mihVnos).
* [curated_mil](curated_mil.md) - One row = one document line (order/invoice line) per company, with ag01 lines credited to a split-sale rep duplicated into two rows, unique on (company_id, milType, milVnos, milListno) plus the split.
* [curated_tbook_quotation](curated_tbook_quotation.md) - One row = the latest revision of one quotation per company, unique on (company_id, Running).

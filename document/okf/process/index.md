# Process

AI address parsing, RLS access map and the Pub/Sub export tables.

# Tables

* [deb_address_data](deb_address_data.md) - One row = the AI-parsed Thai address (sub-district, district, province in Thai and English) of one MAC5 customer (debtor) per company.
* [mart_export_config](mart_export_config.md) - One row = one Data Mart table exported to Pub/Sub, with its source view, topic and the publisher's memory of the last Dataform run it handled.
* [mart_sent_state](mart_sent_state.md) - One row = one data row (by row_key) that a Pub/Sub export table last sent successfully, with its hash and the Dataform invocation that sent it.
* [rls_customer360](rls_customer360.md) - One row = one customer (milCus) with the pipe-delimited lists of every salesperson, section, region, director and product-marketing combination associated with that customer in the transaction fact.

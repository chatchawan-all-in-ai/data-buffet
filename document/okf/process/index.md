# Process

AI address parsing, RLS access maps and the Pub/Sub export tables.

# Tables

* [deb_address_data](deb_address_data.md) - One row = the AI-parsed Thai address (sub-district, district, province in Thai and English) of one MAC5 customer (debtor) per company.
* [mart_export_config](mart_export_config.md) - One row = one Data Mart table exported to Pub/Sub, with its source view, topic, task group, trigger and the publisher's memory of the last Dataform run it handled.
* [mart_sent_state](mart_sent_state.md) - One row = one data row (by row_key) that a Pub/Sub export table last sent successfully, with its hash and the Dataform invocation whose run triggered the publish of the row.
* [rls_customer360](rls_customer360.md) - One row = one customer (milCus) with the pipe-delimited lists of every salesperson, section, region, director and product-marketing combination associated with that customer in the transaction fact.
* [rls_ta_customer](rls_ta_customer.md) - One row = one viewer (employee) x one customer (company + code, or ALL) x one product scope that the viewer may see today, expanded from the org center department portfolios, manager tree and special-access exceptions.

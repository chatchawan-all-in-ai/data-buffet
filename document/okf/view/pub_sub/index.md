# pub_sub

13 cards in BigQuery dataset `pub_sub`.

# Tables

* [export_chqri](export_chqri.md) - One row = one ag01 received cheque (chqtype 1) per receipt (RS) payment line dated 2026; commission set `chqri` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_company](export_company.md) - One row = one ag01 customer; commission set `company` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_company_source](export_company_source.md) - One row = the Data Mart company ag01 that owns the data; commission set `company_source` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_credit_note](export_credit_note.md) - One row = one line of an ag01 credit note (BS) of 2026, not cancelled; commission set `credit_note` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_debit_note](export_debit_note.md) - One row = one line of an ag01 debit note (AS) of 2026, not cancelled; commission set `debit_note` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_dim_company](export_dim_company.md) - One row = one company of dim_company exposed for the Pub/Sub export (data columns without SKs, plus row_key and row_hash).
* [export_invoice](export_invoice.md) - One row = one line of an ag01 invoice (IS) of 2026, not cancelled; commission set `invoice` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_order](export_order.md) - One row = one line of an ag01 sales document of 2026 (all document types, not cancelled); commission set `order` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_receipt](export_receipt.md) - One row = one line of an ag01 receipt (RS) of 2026 per cheque line paying it, document not cancelled; commission set `receipt` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_sell](export_sell.md) - One row = one ag01 salesperson, hidden ones included; commission set `sell` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_status](export_status.md) - One row = one ag01 document status code; commission set `status` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_stk](export_stk.md) - One row = one ag01 product; commission set `stk` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_warehouse](export_warehouse.md) - One row = one ag01 warehouse; commission set `warehouse` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.

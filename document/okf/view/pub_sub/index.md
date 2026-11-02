# pub_sub

22 cards in BigQuery dataset `pub_sub`.

# Tables

* [export_access_exceptions](export_access_exceptions.md) - One row = one special-access scope of a person with the code arrays split to one value per row, exposed for the Pub/Sub export of the TA app table access_exceptions with row_key and row_hash.
* [export_appointments](export_appointments.md) - One row = one seat (person, unit, position, start date) with company_id and the TA zone, exposed for the Pub/Sub export of the TA app table appointments with row_key and row_hash.
* [export_chqri](export_chqri.md) - One row = one ag01 received cheque (chqtype 1) per receipt (RS) payment line dated 2026; commission set `chqri` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_company](export_company.md) - One row = one ag01 customer; commission set `company` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_company_source](export_company_source.md) - One row = the Data Mart company ag01 that owns the data; commission set `company_source` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_credit_note](export_credit_note.md) - One row = one line of an ag01 credit note (BS) of 2026, not cancelled; commission set `credit_note` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_customer_ta_assignments](export_customer_ta_assignments.md) - One row = one customer in the portfolio of one TA for a period, with the customer company and the company of the TA membership it points to, exposed for the Pub/Sub export of the TA app table customer_ta_assignments with row_key and row_hash.
* [export_debit_note](export_debit_note.md) - One row = one line of an ag01 debit note (AS) of 2026, not cancelled; commission set `debit_note` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_dim_company](export_dim_company.md) - One row = one company of dim_company exposed for the Pub/Sub export (data columns without SKs, plus row_key and row_hash).
* [export_employees](export_employees.md) - One row = one person (EmployeeID): everyone in org_center_person plus the people with a special-access row who have no seat, exposed for the Pub/Sub export of the TA app table employees with row_key and row_hash.
* [export_invoice](export_invoice.md) - One row = one line of an ag01 invoice (IS) of 2026, not cancelled; commission set `invoice` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_member_links](export_member_links.md) - One row = one PC to TA link at one branch from one start date, exposed for the Pub/Sub export of the TA app table member_links with row_key and row_hash.
* [export_memberships](export_memberships.md) - One row = one person in one company with all seats folded together, exposed for the Pub/Sub export of the TA app table memberships with row_key and row_hash.
* [export_order](export_order.md) - One row = one line of an ag01 sales document of 2026 (all document types, not cancelled); commission set `order` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_org_levels](export_org_levels.md) - One row = one org level (depth 1-3: division, region, section) of a company that has units, exposed for the Pub/Sub export of the TA app table org_levels with row_key and row_hash.
* [export_org_units](export_org_units.md) - One row = one division, region or section of a company (company rows left out), exposed for the Pub/Sub export of the TA app table org_units with region_code, row_key and row_hash.
* [export_positions](export_positions.md) - One row = one position held by someone in a company, exposed for the Pub/Sub export of the TA app table positions with row_key and row_hash.
* [export_receipt](export_receipt.md) - One row = one line of an ag01 receipt (RS) of 2026 per cheque line paying it, document not cancelled; commission set `receipt` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_sell](export_sell.md) - One row = one ag01 salesperson, hidden ones included; commission set `sell` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_status](export_status.md) - One row = one ag01 document status code; commission set `status` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_stk](export_stk.md) - One row = one ag01 product; commission set `stk` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.
* [export_warehouse](export_warehouse.md) - One row = one ag01 warehouse; commission set `warehouse` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash.

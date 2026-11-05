# process_dataset

5 cards in BigQuery dataset `process_dataset`.

# Tables

* [view_deb_address_data](view_deb_address_data.md) - One row = one match of the AI-parsed invoice address of an ag01 customer (debcode) to a Thai sub-district, district or province, with the geography SKs.
* [view_mih_address_data](view_mih_address_data.md) - One row = one document (mihType + mihVnos) whose AI-parsed address was matched to a Thai sub-district, district or province, with the geography SKs.
* [view_rls_data](view_rls_data.md) - One row = one (employee, restricted attribute, allowed value) entry of the organisation-based row-level-security map for sales managers, plus one CompanyID row per employee.
* [view_rls_sale_data](view_rls_sale_data.md) - One row = one (employee e-mail, restricted attribute, allowed value) entry of the RLS access map for sales employees, combining the org hierarchy with the customers of their sections.
* [view_rls_special_data](view_rls_special_data.md) - One row = one (employee e-mail, restricted attribute, allowed value) entry of the RLS access map for special and marketing employees, defined in mds rather than by the org hierarchy.

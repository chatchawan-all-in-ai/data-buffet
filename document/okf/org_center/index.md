# Org Center

Organisation structure (units, members, people, links, customer portfolios, exceptions, data-quality flags).

# Tables

* [org_center_customer_ta](org_center_customer_ta.md) - Customer portfolio contract.
* [org_center_exception](org_center_exception.md) - One row = one person x company x product scope of a special access exception, copied from the MDS special-RLS table with ALL for unrestricted values and the lists split.
* [org_center_flags](org_center_flags.md) - Data-quality report contract.
* [org_center_link](org_center_link.md) - PC assignment contract.
* [org_center_member](org_center_member.md) - One row = one person holding one position at one unit for a date range (CEO, director, region manager, section manager, TA, or PC).
* [org_center_person](org_center_person.md) - One row = one person (across all companies) in the org center, with name, contact, LINE UUID, companies, current positions and an active flag.
* [org_center_unit](org_center_unit.md) - One row = one organisation unit (company, division, region or section) of one company.

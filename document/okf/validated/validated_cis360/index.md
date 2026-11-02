# validated_cis360

24 cards in BigQuery dataset `validated_cis360`.

# Tables

* [address_type](address_type.md) - One row = one address type from source table `address_type`, unique on (id).
* [category](category.md) - One row = one business category from source table `category`, unique on (id).
* [country](country.md) - One row = one country from source table `country`, unique on (id).
* [customer_address](customer_address.md) - One row = one customer address from source table `customer_address`, unique on (id).
* [customer_profile](customer_profile.md) - One row = one customer profile from source table `customer_profile`, unique on (id).
* [customer_profile_category](customer_profile_category.md) - One row = one business category assigned to a customer profile from source table `customer_profile_category`, unique on (id).
* [customer_profile_nature_business](customer_profile_nature_business.md) - One row = one nature of business assigned to a customer profile from source table `customer_profile_nature_business`, unique on (id).
* [customer_profile_role_business](customer_profile_role_business.md) - One row = one business role assigned to a customer profile from source table `customer_profile_role_business`, unique on (id).
* [customer_profile_tag](customer_profile_tag.md) - One row = one tag assigned to a customer profile from source table `customer_profile_tag`, unique on (id).
* [customer_profile_type](customer_profile_type.md) - One row = one customer profile type from source table `customer_profile_type`, unique on (id).
* [customer_status](customer_status.md) - One row = one customer status from source table `customer_status`, unique on (id).
* [customer_to_customer](customer_to_customer.md) - One row = one relationship between two customer profiles from source table `customer_to_customer`, unique on (id).
* [customer_to_platform](customer_to_platform.md) - One row = one customer-platform link from source table `customer_to_platform`, unique on (id).
* [customer_to_transaction](customer_to_transaction.md) - One row = one buyer-seller transaction from source table `customer_to_transaction`, unique on (id).
* [customer_type](customer_type.md) - One row = one customer type from source table `customer_type`, unique on (id).
* [district](district.md) - One row = one district from source table `district`, unique on (id).
* [juristic_profile](juristic_profile.md) - One row = one juristic profile of a customer from source table `juristic_profile`, unique on (id).
* [juristic_type](juristic_type.md) - One row = one juristic entity type from source table `juristic_type`, unique on (id).
* [nature_business](nature_business.md) - One row = one nature of business from source table `nature_business`, unique on (id).
* [organize_type](organize_type.md) - One row = one organization type from source table `organize_type`, unique on (id).
* [province](province.md) - One row = one province from source table `province`, unique on (id).
* [role_business](role_business.md) - One row = one business role from source table `role_business`, unique on (id).
* [sub_district](sub_district.md) - One row = one sub-district from source table `sub_district`, unique on (id).
* [zipcode](zipcode.md) - One row = one postal code for a sub-district from source table `zipcode`, unique on (id).

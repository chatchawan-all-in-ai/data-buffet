# validated_master_sku

33 cards in BigQuery dataset `validated_master_sku`.

# Tables

* [brand_translations](brand_translations.md) - One row = one brand name in one language from source table `brand_translations`, unique on (brand_id, language_id).
* [brand_vendors](brand_vendors.md) - One row = one brand supplied by one vendor from source table `brand_vendors`, unique on (id).
* [brands](brands.md) - One row = one brand from source table `brands`, unique on (id).
* [categories](categories.md) - One row = one product category from source table `categories`, unique on (id).
* [category_translations](category_translations.md) - One row = one category name in one language from source table `category_translations`, unique on (category_id, language_id).
* [common_code_translations](common_code_translations.md) - One row = one code name in one language from source table `common_code_translations`, unique on (common_code_id, language_id).
* [common_codes](common_codes.md) - One row = one code value in one code list from source table `common_codes`, unique on (id).
* [product_translations](product_translations.md) - One row = one product text in one language from source table `product_translations`, unique on (product_id, language_id).
* [products](products.md) - One row = one product (SKU) from source table `products`, unique on (id).
* [spec_attribute_translations](spec_attribute_translations.md) - One row = one specification attribute name in one language from source table `spec_attribute_translations`, unique on (spec_attribute_id, language_id).
* [spec_attributes](spec_attributes.md) - One row = one specification attribute from source table `spec_attributes`, unique on (id).
* [spec_group_translations](spec_group_translations.md) - One row = one specification group name in one language from source table `spec_group_translations`, unique on (spec_group_id, language_id).
* [spec_groups](spec_groups.md) - One row = one specification group from source table `spec_groups`, unique on (id).
* [specifications](specifications.md) - One row = one attribute assigned to one specification group from source table `specifications`, unique on (group_id, attribute_id).
* [synonyms](synonyms.md) - One row = one search term with its synonyms from source table `synonyms`, unique on (id).
* [vendors](vendors.md) - One row = one vendor from source table `vendors`, unique on (id).
* [audit_logs](audit_logs.md) - One row per audit events for entities in the master_sku 3.0 product master from source table `audit_logs`, unique on (id).
* [business_unit_translations](business_unit_translations.md) - One row per localized business unit names and descriptions from source table `business_unit_translations`, unique on (business_unit_id, language_id).
* [business_units](business_units.md) - One row per business units configured in the master_sku 3.0 source from source table `business_units`, unique on (id).
* [channels](channels.md) - One row per sales channels configured in the product master from source table `channels`, unique on (id).
* [customers](customers.md) - One row per customer records linked to product information from source table `customers`, unique on (id).
* [functional_group_translations](functional_group_translations.md) - One row per localized names and descriptions for product functional groups from source table `functional_group_translations`, unique on (functional_group_id, language_id).
* [functional_groups](functional_groups.md) - One row per functional group hierarchy used by the product master from source table `functional_groups`, unique on (id).
* [product_assets](product_assets.md) - One row per digital assets and files associated with products or other source references from source table `product_assets`, unique on (id).
* [product_channel_prices](product_channel_prices.md) - One row per product price by sales channel, business unit, and effective date from source table `product_channel_prices`, unique on (product_id, sales_channel_id, business_unit_id, effective_date).
* [product_channels](product_channels.md) - One row per product-to-sales-channel assignments from source table `product_channels`, unique on (product_id, sales_channel_id).
* [product_customers](product_customers.md) - One row per customer-specific product record from source table `product_customers`, unique on (id).
* [product_codes](product_codes.md) - One row per alternate business codes associated with products from source table `product_codes`, unique on (id).
* [product_groups](product_groups.md) - One row per named groups used to organize products from source table `product_groups`, unique on (id).
* [product_vendors](product_vendors.md) - One row per product-to-vendor assignments and vendor-side product details from source table `product_vendors`, unique on (id).
* [variant_definitions](variant_definitions.md) - One row per definitions for product or media variants from source table `variant_definitions`, unique on (id).
* [users](users.md) - One row per user accounts registered in the master_sku source from source table `users`, unique on (id).
* [user_preferences](user_preferences.md) - One row per preference settings associated with source users from source table `user_preferences`, unique on (id).

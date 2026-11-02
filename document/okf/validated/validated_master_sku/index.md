# validated_master_sku

16 cards in BigQuery dataset `validated_master_sku`.

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

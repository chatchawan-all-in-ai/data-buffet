# validated_master_sku

16 cards in BigQuery dataset `validated_master_sku`.

# Tables

* [brand_translations](brand_translations.md) - One row = one cleaned copy of the source table `brand_translations`, unique on (brand_id, language_id).
* [brand_vendors](brand_vendors.md) - One row = one cleaned copy of the source table `brand_vendors`, unique on (id).
* [brands](brands.md) - One row = one cleaned copy of the source table `brands`, unique on (id).
* [categories](categories.md) - One row = one cleaned copy of the source table `categories`, unique on (id).
* [category_translations](category_translations.md) - One row = one cleaned copy of the source table `category_translations`, unique on (category_id, language_id).
* [common_code_translations](common_code_translations.md) - One row = one cleaned copy of the source table `common_code_translations`, unique on (common_code_id, language_id).
* [common_codes](common_codes.md) - One row = one cleaned copy of the source table `common_codes`, unique on (id).
* [product_translations](product_translations.md) - One row = one cleaned copy of the source table `product_translations`, unique on (product_id, language_id).
* [products](products.md) - One row = one cleaned copy of the source table `products`, unique on (id).
* [spec_attribute_translations](spec_attribute_translations.md) - One row = one cleaned copy of the source table `spec_attribute_translations`, unique on (spec_attribute_id, language_id).
* [spec_attributes](spec_attributes.md) - One row = one cleaned copy of the source table `spec_attributes`, unique on (id).
* [spec_group_translations](spec_group_translations.md) - One row = one cleaned copy of the source table `spec_group_translations`, unique on (spec_group_id, language_id).
* [spec_groups](spec_groups.md) - One row = one cleaned copy of the source table `spec_groups`, unique on (id).
* [specifications](specifications.md) - One row = one cleaned copy of the source table `specifications`, unique on (group_id, attribute_id).
* [synonyms](synonyms.md) - One row = one cleaned copy of the source table `synonyms`, unique on (id).
* [vendors](vendors.md) - One row = one cleaned copy of the source table `vendors`, unique on (id).

# Directory Update Log

## 2026-11-08 (formula datetime parsing)

* **Update**: Corrected formula date-field types in the [raw line](initial/raw_derp/inventory_formula_line.md#schema), [raw version](initial/raw_derp/inventory_formula_versions.md#schema), [validated line](validated/validated_derp/inventory_formula_line.md#schema) and [validated version](validated/validated_derp/inventory_formula_versions.md#schema) cards.

## 2026-11-08 (MASTER_SKU expansion)

* **Creation**: Added the three remaining MASTER_SKU raw and validated table cards; refreshed their dataset indexes and the initial/validated inventories.

* **Creation**: Added the 14 new table cards linked from the [raw MASTER_SKU index](initial/raw_master_sku/index.md) and [validated MASTER_SKU index](validated/validated_master_sku/index.md), and refreshed their dataset and layer indexes.

* **Update**: Applied review corrections to stable fact row keys, full BillingSK natural keys, invoice order-occurrence selection and affected consumer cards.
* **Update**: Documented stable row keys for all 11 scoped facts and refreshed the affected fact OKF cards.
* **Update**: Updated the seven retained fact cards for stable row keys and the OKF cards of their direct consumers.
* **Update**: Aligned the shared reader rule with omitted empty reader lists, used the TITAN series code in the product-attribute example, and replaced stale export and aggregation descriptions with pointers to the source cards.

* **Update**: Clarified CIS360 `ag01` profile matching, stored aging-history values, ordered latest-section rules and transaction join multiplicity in the view cards and their exports.

## 2026-11-08 (D-ERP raw and validated tables)

* **Creation**: Added 20 cards for the 10 combo-set, payment, formula and price-sync tables; updated the `raw_derp` and `validated_derp` indexes (51 cards each) and refreshed the source inventories.
* **Update**: Specified timestamp-first deduplication order in the ten new validated cards and replaced raw-card deduplication summaries with pointers to those cards.

* **Update**: Corrected the [view cards](view/index.md) and [Pub/Sub export cards](view/pub_sub/index.md): table facts, SQL examples, direct readers and export contracts; removed deploy lines and standardized `Read by:` wording.
* **Update**: Second-round corrections to the scoped core cards and indexes: fixed remaining report findings, standardized `Read by:` to direct readers, documented that rule, and refreshed `generated.at` on edited cards.
* **Update**: Expanded the six TF commission export views and their cards to include all years for company `ag01`.

## 2026-11-05 (core card review fixes)

* **Update**: Second-round corrections to validated and initial cards and indexes: reader wording and its [shared rule](README.md#rule), removal of indirect-reader prose from raw cards, index descriptions, refreshed edit metadata and SALEOUT_MDT details.
* **Creation**: Added the [curated_derp](curated/curated_derp/index.md) dataset with the [curated_invoice_line_cost](curated/curated_derp/curated_invoice_line_cost.md) and [curated_journal_invoice](curated/curated_derp/curated_journal_invoice.md) cards (curated 16 cards).
* **Update**: Review corrections to the dimension, fact, curated, org_center, process and cdc cards and their indexes: grain and key wording, column meanings, formulas, examples, `Read by:` lines (including the Pub/Sub export views), unified wording for repeated columns, and removal of warnings, history and dated observations.

## 2026-11-05 (TA customer dependency order)

* **Update**: [rls_ta_customer](process/rls_ta_customer.md) now waits for `update_sk_sale_rep_group` to fill `SectionSK` before rebuilding access.

## 2026-11-05 (view card review fixes)

* **Update**: Review corrections to the [dimension_view](view/dimension_view/index.md), [fact_view](view/fact_view/index.md), [onetime](view/onetime/index.md), [process_dataset](view/process_dataset/index.md) and [bridge_dataset](view/bridge_dataset/index.md) cards: grain and key descriptions, column lists following the sqlx, column meanings and formulas, reader and export lists; deploy lines and caveats removed; refreshed edit metadata on changed cards.

## 2026-11-05 (validated and initial card review fixes)

* **Update**: Review corrections to the [validated](validated/index.md) and [initial](initial/index.md) cards: `company_id` meaning per actual UNION branches, no dedup sentence on tables without a key, the added logic of `chq`, `mih`, `mil`, `stg`, `tbook_quotation`, `saleout_dh`, `saleout_gb`, `saleout_hp` and `sale_by_branch_detail`, the readers in Used by (`curated_derp` and the `pub_sub` export views), and removal of time-dependent wording (`BACKFILL_DAYS` value, dates, `(none)` partition).

## 2026-11-05 (pub_sub export card review fixes)

* **Update**: Review corrections to the [Pub/Sub export cards and index](view/pub_sub/index.md), including grain and key descriptions, column meanings, formulas and publishing metadata; refreshed edit metadata on changed cards.
* **Update**: Corrected the access-source description in [rls_ta_customer](process/rls_ta_customer.md#schema); the export card points to that definition.

## 2026-11-05 (TA department binding)

* **Update**: Revised the [customer portfolio](org_center/org_center_customer_ta.md), [PC assignment](org_center/org_center_link.md), [membership](org_center/org_center_member.md), [flags](org_center/org_center_flags.md), [customer access](process/rls_ta_customer.md), [customer assignment export](view/pub_sub/export_customer_ta_assignments.md) and [PC link export](view/pub_sub/export_member_links.md) contracts.

## 2026-11-03 (org center field changes)
* **Update**: `org_center_person` card: new column `line_uuid` (MDS EMPLOYEE_INFO LineUUID); `company_ids` -> `company_id`, `position_codes` -> `position_code`.
* **Update**: `org_center_member` card: `department_ids` -> `department_id`; column `company_name` dropped. `org_center_link` card: column `company_name` dropped.
* **Update**: `org_center_exception` card: `director_codes` -> `director_code`, `region_codes` -> `region_code`, `section_codes` -> `section_code`.
* **Update**: `export_employees` card: new column `line_uuid`.
* **Update**: removed the "Approximate size" line from every card that had one, and the row-count phrases from the cards that carried them (tables rebuild daily, so counts go stale).

## 2026-11-03 (Cloud Run publisher)
* **Update**: `mart_export_config` card: new column `task_group` (ninth), the config MERGE now also refreshes it, claim expiry 30 -> 35 minutes, publisher is the Cloud Run jobs instead of the Cloud Workflow.
* **Update**: `mart_sent_state` card: writer is the Cloud Run send job (every 1,000,000 sent rows and at the end of a table); size corrected to about 1.38 million rows, 156 MB.
* **Update**: the 55 `pub_sub` export view cards: the publisher named in the description is the Cloud Run publisher.

## 2026-11-03 (AI team sample tables Pub/Sub export)
* **Creation**: Added 33 cards for the export views of the AI team sample tables in `pub_sub` (export_dim_aging_rang, export_dim_calendar, export_dim_customer_segment, export_dim_doctype, export_dim_payment, export_dim_product_master_fc, export_dim_product_series, export_dim_project, export_dim_pump_information, export_dim_quotation, export_dim_section_last, export_dim_target_product_group_by_sale_dayofwork, export_view_dim_aging_history, export_view_dim_channel, export_view_dim_company, export_view_dim_customer, export_view_dim_customer_report_info, export_view_dim_invoice, export_view_dim_order, export_view_dim_product_master, export_view_dim_product_mkt, export_view_dim_sale_representative_last, export_fact_delivery, export_fact_order, export_fact_quotation, export_fact_transaction_delivery, export_view_fact_transcation, export_mds_data_org_ols_center, export_product_attribute, export_view_rls_sale_data, export_brand, export_rls_ta_customer, export_mds_data_ta_dashboard_display_control; pub_sub 55 cards, view 95 cards).
* **Update**: `mart_export_config` card: 55 rows (dim_company, 12 commission sets, 9 TA org sets, 33 AI team sample tables).

## 2026-11-02 (TA org Pub/Sub export)
* **Creation**: Added 9 cards for the TA app org export views in `pub_sub` (export_org_levels, export_org_units, export_positions, export_employees, export_memberships, export_appointments, export_member_links, export_access_exceptions, export_customer_ta_assignments; pub_sub 22 cards, view 62 cards).
* **Update**: `mart_export_config` card: 22 rows (dim_company, 12 commission sets, 9 TA org sets).

## 2026-11-02 (commission Pub/Sub export)
* **Creation**: Added 12 cards for the commission export views of the TF team in `pub_sub` (export_order, export_invoice, export_credit_note, export_debit_note, export_receipt, export_chqri, export_status, export_company, export_sell, export_warehouse, export_stk, export_company_source; pub_sub 13 cards, view 53 cards).
* **Update**: Corrected the config card's sent-state dependency and claim semantics; linked the first-load procedure to its owner. `mart_export_config` card: new `trigger_scheduler` and `seeded_at` columns, durable not-yet-seeded marker for new export tables and backfill from existing sent state for dim_company, 13 rows; `mart_sent_state` card: seed only during the captain-dated manual Cloud Shell snapshot, with files from the same snapshot.

## 2026-11-02
* **Removal**: Removed the `rls_ta_sale` card and process index entry with its Dataform definition.
* **Creation**: Added the `rls_ta_customer` card (process 5 cards).
* **Update**: Added the `region_code` column to the `org_center_unit` card.

## 2026-11-01
* **Creation**: Added the `org_center_customer_ta` card (org_center 6 cards).
* **Creation**: Added the `org_center_exception` card (org_center 7 cards); updated the `org_center_flags` card for the EXCEPTION_NO_EMPLOYEE rule.

## 2026-11-01 (column descriptions)
* **Update**: Replaced every undocumented or hedged column meaning (11,378 schema rows in 500 cards) with a plain description taken from code use, wiki pages, column names and sampled data, and rewrote vague column text in the derived layers (11,701 rows changed in 521 cards). Identical source columns share one text across the MAC5 company datasets and the raw and validated layers. Raw and validated card descriptions, `# What it is` texts and their index lines now state what each table holds.

## 2026-10-31 (location keys)
* **Update**: Added `project_id`, `dataset_id` and `table_id` frontmatter keys to all 605 cards (values match the `resource` URL; 598 confirmed against BigQuery `INFORMATION_SCHEMA`, the 7 `validated_mac5` tables mip, rcv, stg_report, tbook_payin, tbook_quotation, tdis_approveorder and tdis_mail are defined in the repo but not built in BigQuery yet); README card layout lists them.

## 2026-10-31
* **Creation**: Established the bundle with 605 cards (initial 261, validated 190, curated 14, dimension 71, fact 18, view 41, process 4, cdc 1, org_center 5).
* **Creation**: Added `index.md` files for the bundle, each layer and each dataset folder.

## 2026-11-08 (target by sale rebuild)
* **Update**: Updated the [target-by-sale contract](dimension/dim_target_product_group_by_sale.md#grain-and-key) and its consumer reference for the restored rebuild.

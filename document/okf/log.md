# Directory Update Log

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

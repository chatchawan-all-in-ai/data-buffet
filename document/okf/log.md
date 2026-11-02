# Directory Update Log

## 2026-11-02
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

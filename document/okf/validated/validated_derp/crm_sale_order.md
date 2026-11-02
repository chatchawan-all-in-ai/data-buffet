---
type: BigQuery Table
title: "crm_sale_order"
description: "One row = one sale order from source table `crm_sale_order`, unique on (sale_order_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_sale_order`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Sale order headers of the DERP CRM/ERP: customer, sales channel, payment terms, amounts, VAT, document and status, one row per sale order.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_id` | STRING | Unique identifier (UUID) of the sale order. |
| `so_no` | STRING | Sale order number (e.g. `A2610000106`; prefix follows the sales channel), NULL while the order is a draft. |
| `is_draft` | BOOL | TRUE while the sale order is still a draft. |
| `status` | STRING | Sale order workflow status code (`20` = draft, `54` = submitted for approval, `83` = waiting for PO mapping, `22` = approved, `25` = waiting for credit approval, `26` = credit approved, `27` = rejected, `28` = cancelled, `60` = edited after finalization, `64` = pay-in approved). |
| `payment_type` | STRING | Payment type of the order (`CASH`, `CREDIT` or `OTHER`). |
| `rev_no` | INT64 | Revision number of the sale order, starting at 1 and increased when a finalized order is edited. |
| `is_latest` | BOOL | TRUE when this is the latest revision of the sale order. |
| `so_date` | DATETIME | Sale order date and time. |
| `expected_delivery_date` | DATETIME | Expected delivery date of the order. |
| `routed_to_credit_approve` | BOOL | TRUE when the order was routed to credit approval. |
| `deposit_fully_paid` | BOOL | TRUE when all deposit installments have been paid. |
| `quotation_id` | STRING | Identifier of the source quotation (`crm_quotation`). |
| `quotation_no` | STRING | Number of the source quotation (e.g. `MDT261000057`). |
| `sale_channel_1_id` | STRING | Identifier of the level-1 sales channel. |
| `sale_channel_1_code` | STRING | Level-1 sales channel code (e.g. `MDT` = modern trade, `A` = agent Bangkok, `AR` = agent upcountry, `CRC` = SCG-affiliated stores). |
| `sale_channel_2_id` | STRING | Identifier of the level-2 sales channel. |
| `sale_channel_2_code` | STRING | Level-2 sales channel code. |
| `sale_channel_3_id` | STRING | Identifier of the level-3 sales channel. |
| `sale_channel_3_code` | STRING | Level-3 sales channel code. |
| `sale_channel_path_id` | STRING | Identifier of the full sales channel path. |
| `sale_channel_path_code` | STRING | Sales channel path code joining the channel levels with `/` (e.g. `MDT/`). |
| `sale_channel_path_name` | STRING | Sales channel path name (e.g. Modern Trade (MDT)). |
| `customer_master_id` | STRING | Identifier of the customer (`crm_customer_master`). |
| `customer_code` | STRING | Customer code (e.g. `C0000034`). |
| `customer_address_id` | STRING | Identifier of the customer address used on the order. |
| `customer_address_code` | STRING | Customer code of the address used on the order. |
| `invoice_account_id` | STRING | Identifier of the customer account billed for the order. |
| `invoice_account_code` | STRING | Customer code of the account billed for the order. |
| `order_account_id` | STRING | Identifier of the customer account that placed the order. |
| `order_account_code` | STRING | Customer code of the account that placed the order. |
| `delivery_account_id` | STRING | Identifier of the customer account that receives the delivery. |
| `delivery_account_code` | STRING | Customer code of the account that receives the delivery. |
| `project_id` | STRING | Identifier of the customer project the order belongs to. |
| `project_code` | STRING | Code of the customer project the order belongs to (e.g. `PRJ0003`). |
| `target_group_id` | STRING | Identifier of the customer target group. |
| `target_group_code` | STRING | Customer target group code (e.g. `TT`, `DD`, `DT`). |
| `payment_method_id` | STRING | Identifier of the payment method. |
| `payment_method_code` | STRING | Payment method code (e.g. `BANK_TRANSFER`, `CASH`, `CHEQUE`, `CREDIT_LIMIT`, `BILL_PAYMENT`, `OTHER_FINANCE`). |
| `payment_method_name` | STRING | Payment method name in Thai. |
| `payment_term_id` | STRING | Identifier of the payment term. |
| `payment_term_code` | STRING | Payment term code (`N000`/`N030`/`N060` = pay 0/30/60 days after delivery, `N888` = no term). |
| `payment_term_name` | STRING | Payment term description in Thai (e.g. pay 60 days after delivery). |
| `payment_term_other` | STRING | Free-text payment term entered when no standard term applies. |
| `payment_condition_id` | STRING | Identifier of the payment condition. |
| `payment_condition_code` | STRING | Payment condition code (e.g. `BP_CRM` = by billing cycle, `BFF_LMS` = before delivery, `NOW_LMS` = on delivery, `AFT_LMS` = after delivery, `OTHER`). |
| `payment_condition_name` | STRING | Payment condition description in Thai. |
| `payment_condition_other` | STRING | Free-text payment condition entered when no standard condition applies. |
| `po_ref` | STRING | Customer purchase order (PO) number referenced by the order. |
| `is_vat` | INT64 | VAT flag of the order (`1` = VAT applies, `0` = not set). |
| `vat_code` | STRING | VAT code (e.g. `VAT7`). |
| `vat_name` | STRING | VAT name (e.g. `VAT 7%`). |
| `vat_rate` | FLOAT64 | VAT rate in percent (e.g. `7`). |
| `total_amount` | FLOAT64 | Order amount before trade discount and VAT (THB). |
| `trade_discount_amount` | FLOAT64 | Trade discount amount of the order (THB). |
| `subtotal_before_vat` | FLOAT64 | Order amount after trade discount and before VAT (THB). |
| `vat_amount` | FLOAT64 | VAT amount of the order (THB). |
| `grand_total_amount` | FLOAT64 | Order total including VAT (THB). |
| `deposit_amount` | FLOAT64 | Total deposit required for the order (THB). |
| `remark_invoice` | STRING | Remark printed on the invoice. |
| `remark_production` | STRING | Remark for production or approval consideration. |
| `remark_project` | STRING | Remark about the project or special instructions (e.g. PO expiry note). |
| `remark_project_detail` | STRING | Detailed remark about the project. |
| `remark_payment` | STRING | Remark about payment. |
| `remark_payment_bill` | STRING | Remark about billing for payment. |
| `full_text_search` | STRING | Concatenated search text (order and quotation numbers, customer code and name, salesperson) used for searching. |
| `mac5_id` | STRING | Identifier of the matching record in the MAC5 ERP. |
| `mac5_code` | STRING | Document code of the matching record in the MAC5 ERP. |
| `d365_id` | STRING | Identifier of the matching record in Microsoft Dynamics 365. |
| `d365_code` | STRING | Document code of the matching record in Microsoft Dynamics 365. |
| `is_active` | BOOL | TRUE while the record is active. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `customer_tel` | STRING | Customer phone number on the order. |
| `customer_email` | STRING | Customer email address on the order. |
| `customer_address_text` | STRING | Customer address text on the order. |
| `qt_type` | STRING | Type of the source quotation (`QT` = standard quotation, `MDT` = modern trade). |
| `customer_group_id` | STRING | Identifier of the customer group. |
| `customer_group_code` | STRING | Customer group code (e.g. `HP`, `TW`, `GB`). |
| `delivery_start_date` | DATETIME | Start date of the delivery window. |
| `delivery_end_date` | DATETIME | End date of the delivery window. |
| `delivery_mode` | STRING | Delivery mode (`single` = one delivery, `split` = several delivery rounds). |
| `delivery_doc_code` | STRING | Comma-separated codes of documents sent with the delivery (e.g. `DOC_INV`, `DOC_CUST_DO`, `DOC_ETAX`). |
| `delivery_doc_id` | STRING | Identifier of the document set sent with the delivery. |
| `doc_delivery_address_type` | STRING | Type of address documents are sent to (`shipping` or `other`). |
| `doc_delivery_address_text` | STRING | Address text for sending documents. |
| `order_delivery_type` | STRING | Delivery type of the order (`DIRECT`, `FORWARD` or `NO_LOGISTIC`). |
| `site_id` | STRING | Identifier of the shipping site (plant or warehouse). |
| `site_code` | STRING | Code of the shipping site (plant or warehouse, e.g. `KTB`, `KK1`, `LP1`). |
| `doc_with_tax_invoice` | BOOL | TRUE when a tax invoice is sent with the goods. |
| `doc_with_po` | BOOL | TRUE when the customer PO is sent with the goods. |
| `doc_with_customer_do` | BOOL | TRUE when the customer delivery order is sent with the goods. |
| `doc_with_etax` | BOOL | TRUE when an e-tax invoice is issued. |
| `doc_delivery_subdistrict` | STRING | Sub-district of the document delivery address. |
| `doc_delivery_district` | STRING | District of the document delivery address. |
| `doc_delivery_province` | STRING | Province of the document delivery address. |
| `doc_delivery_postal_code` | STRING | Postal code of the document delivery address. |
| `doc_delivery_address_full` | STRING | Full document delivery address. |
| `doc_delivery_latitude` | FLOAT64 | Latitude of the document delivery address. |
| `doc_delivery_longitude` | FLOAT64 | Longitude of the document delivery address. |
| `doc_delivery_map_url` | STRING | Map URL of the document delivery address. |
| `doc_delivery_subdistrict_code` | STRING | Sub-district code of the document delivery address. |
| `doc_delivery_district_code` | STRING | District code of the document delivery address. |
| `doc_delivery_province_code` | STRING | Province code of the document delivery address. |
| `doc_delivery_country_code` | STRING | Country code of the document delivery address (e.g. `THA`). |
| `remaining_amount` | FLOAT64 | Order amount still unpaid (THB). |
| `currency_code` | STRING | Currency code (e.g. `THB`). |
| `wht_base` | FLOAT64 | Withholding tax base amount (THB). |
| `wht_rate` | FLOAT64 | Withholding tax rate in percent. |
| `wht_amount` | FLOAT64 | Withholding tax amount (THB). |
| `net_payable` | FLOAT64 | Net amount payable by the customer after withholding tax (THB). |
| `qt_trade_discount_amount` | FLOAT64 | Trade discount amount carried over from the quotation (THB). |
| `is_qt_discount_carrier` | BOOL | TRUE when this order carries the quotation-level trade discount. |
| `po_expire_date` | DATE | Expiry date of the customer PO. |
| `reference_doc_1` | STRING | First reference document number. |
| `reference_doc_2` | STRING | Second reference document number. |
| `job_code` | STRING | Customer job code (e.g. `HOME`, `SHOP`). |
| `referrer_code` | STRING | Code of the person who referred the order. |
| `referrer_name` | STRING | Name of the person who referred the order. |
| `primary_sales_id` | STRING | Identifier of the primary salesperson of the order. |
| `primary_sales_code` | STRING | Employee code of the primary salesperson of the order. |
| `primary_sales_name` | STRING | Name of the primary salesperson of the order. |
| `delivery_status` | STRING | Delivery status of the order (`NOT_DELIVERED`, `PARTIAL`). |
| `sub_contract_id` | STRING | Identifier of the subcontract linked to the order. |
| `sub_contract_owner_name` | STRING | Name of the subcontract owner. |
| `paid_total_amount` | FLOAT64 | Total amount paid so far (THB). |
| `outstanding_amount` | FLOAT64 | Order amount still outstanding (THB). |
| `deposit_outstanding_amount` | FLOAT64 | Deposit amount still outstanding (THB). |
| `payment_status` | STRING | Payment status of the order (`UNPAID`, `PARTIAL`, `PAID`, `OVERPAID`). |
| `next_due_date` | DATE | Next payment due date. |
| `customer_invoice_account_id` | STRING | Identifier of the customer account billed for the order. |
| `customer_invoice_account_code` | STRING | Customer code of the account billed for the order. |
| `customer_invoice_address_id` | STRING | Identifier of the billing address. |
| `customer_order_account_id` | STRING | Identifier of the customer account that placed the order. |
| `customer_order_account_code` | STRING | Customer code of the account that placed the order. |
| `customer_order_address_id` | STRING | Identifier of the ordering customer's address. |
| `customer_delivery_address_id` | STRING | Identifier of the delivery address. |
| `allkonm_order_no` | STRING | Order number in the AllkonM ordering platform for orders created there. |
| `allkonm_sub_order_no` | STRING | Sub-order number in the AllkonM ordering platform. |
| `order_channel` | STRING | Channel the order was created in (`DERP` or `AllkonM`). |
| `order_type` | STRING | Order type for service orders (Thai text, e.g. product service). |
| `customer_known_as` | STRING | Name the customer is known by. |
| `allkonm_tran_amount` | FLOAT64 | Transaction amount from the AllkonM platform (THB). |
| `so_creation_type` | STRING | How the sale order was created (`MAPPING_PO` = from a customer PO, `SO_ADMIN_MANUAL` = entered manually by admin). |
| `qt_discount_base_amount` | FLOAT64 | Base amount used to share the quotation discount across orders (THB). |
| `qt_discount_ratio` | FLOAT64 | Share of the quotation discount applied to this order (0 to 1). |
| `so_approver_type` | STRING | Type of approver for the order (`SALE_MANAGER` or `ADMIN_DELEGATE`). |
| `doc_requirement_code` | STRING | Required supporting document (`PO`, `PO_OR_MEMO`, `NONE`). |
| `doc_requirement_reason` | STRING | Reason for the document requirement (e.g. `AGENT_CASH`, `CHANNEL_PO`, `AGENT_CREDIT`). |
| `po_doc_status` | STRING | Status of the customer PO document (`PO_PENDING`, `PO_COMPLETE`, `NOT_REQUIRED`). |
| `po_doc_status_at` | DATETIME | Timestamp when the PO document status last changed. |
| `billing_type` | STRING | Billing type (`BILL` = billed by invoice, `NONE`). |
| `po_date` | DATE | Date of the customer PO. |
| `vat_source` | STRING | Source of the VAT setting (`CUSTOMER` or `MANUAL`). |
| `vat_change_reason` | STRING | Reason the VAT setting was changed manually. |
| `vat_changed_by` | STRING | Identifier of the user who changed the VAT setting. |
| `vat_changed_by_name` | STRING | Display name of the user who changed the VAT setting. |
| `vat_changed_at` | DATETIME | Timestamp when the VAT setting was changed. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order](/initial/raw_derp/crm_sale_order.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,105 rows, 6.9 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order`
GROUP BY sale_order_id
HAVING n > 1
```

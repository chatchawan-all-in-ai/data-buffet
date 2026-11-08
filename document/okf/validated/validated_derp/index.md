# validated_derp

51 cards in BigQuery dataset `validated_derp`.

# Tables

* [crm_business_unit](crm_business_unit.md) - One row = one business unit node from source table `crm_business_unit`, unique on (business_unit_id).
* [crm_combo_set](crm_combo_set.md) - One row = one combo-set header from source table `crm_combo_set`, unique on (combo_set_id).
* [crm_combo_set_customer](crm_combo_set_customer.md) - One row = one customer entitlement for a combo set from source table `crm_combo_set_customer`, unique on (combo_set_customer_id).
* [crm_combo_set_item](crm_combo_set_item.md) - One row = one product line within a combo set from source table `crm_combo_set_item`, unique on (combo_set_item_id).
* [crm_combo_set_sale_territory](crm_combo_set_sale_territory.md) - One row = one sales-territory assignment to a combo set from source table `crm_combo_set_sale_territory`, unique on (combo_set_sale_territory_id).
* [crm_customer_address](crm_customer_address.md) - One row = one customer address from source table `crm_customer_address`, unique on (customer_address_id).
* [crm_customer_contact](crm_customer_contact.md) - One row = one customer contact from source table `crm_customer_contact`, unique on (customer_contact_id).
* [crm_customer_contact_channels](crm_customer_contact_channels.md) - One row = one contact channel of a customer from source table `crm_customer_contact_channels`, unique on (customer_contact_channels_id).
* [crm_customer_credit](crm_customer_credit.md) - One row = one customer credit record from source table `crm_customer_credit`, unique on (customer_credit_id).
* [crm_customer_data_zone](crm_customer_data_zone.md) - One row = one assignment of a customer to a data zone from source table `crm_customer_data_zone`, unique on (customer_data_zone_id).
* [crm_customer_master](crm_customer_master.md) - One row = one customer from source table `crm_customer_master`, unique on (customer_master_id).
* [crm_customer_segment](crm_customer_segment.md) - One row = one customer segment record from source table `crm_customer_segment`, unique on (customer_segment_id).
* [crm_customer_stores](crm_customer_stores.md) - One row = one customer store from source table `crm_customer_stores`, unique on (customer_stores_id).
* [crm_data_zone](crm_data_zone.md) - One row = one data zone node from source table `crm_data_zone`, unique on (data_zone_id).
* [crm_master_payment_condition](crm_master_payment_condition.md) - One row = one payment condition from source table `crm_master_payment_condition`, unique on (master_payment_condition_id).
* [crm_master_payment_method](crm_master_payment_method.md) - One row = one payment method from source table `crm_master_payment_method`, unique on (master_payment_method_id).
* [crm_master_payment_term](crm_master_payment_term.md) - One row = one payment term from source table `crm_master_payment_term`, unique on (master_payment_term_id).
* [crm_nd_sd_price](crm_nd_sd_price.md) - One row = one ND/SD price record for a product from source table `crm_nd_sd_price`, unique on (nd_sd_price_id).
* [crm_nd_sd_price_territory_group](crm_nd_sd_price_territory_group.md) - One row = one link between an ND/SD price and a sales territory group from source table `crm_nd_sd_price_territory_group`, unique on (nd_sd_price_territory_group_id).
* [crm_nd_sd_price_zone](crm_nd_sd_price_zone.md) - One row = one link between an ND/SD price and a data zone from source table `crm_nd_sd_price_zone`, unique on (nd_sd_price_zone_id).
* [crm_quotation](crm_quotation.md) - One row = one quotation (latest revision) from source table `crm_quotation`, unique on (quotation_id).
* [crm_quotation_delivery](crm_quotation_delivery.md) - One row = one delivery round of a quotation from source table `crm_quotation_delivery`, unique on (quotation_delivery_id).
* [crm_quotation_delivery_detail](crm_quotation_delivery_detail.md) - One row = one product line of a quotation delivery round from source table `crm_quotation_delivery_detail`, unique on (quotation_delivery_detail_id).
* [crm_quotation_detail](crm_quotation_detail.md) - One row = one quotation line from source table `crm_quotation_detail`, unique on (quotation_detail_id).
* [crm_quotation_history](crm_quotation_history.md) - One row = one snapshot of a quotation at a revision from source table `crm_quotation_history`, unique on (quotation_history_id).
* [crm_quotation_sale](crm_quotation_sale.md) - One row = one salesperson on a quotation from source table `crm_quotation_sale`, unique on (quotation_sale_id).
* [crm_sale_order](crm_sale_order.md) - One row = one sale order from source table `crm_sale_order`, unique on (sale_order_id).
* [crm_sale_order_approval_log](crm_sale_order_approval_log.md) - One row = one approval action on a sale order from source table `crm_sale_order_approval_log`, unique on (sale_order_approval_log_id).
* [crm_sale_order_approver](crm_sale_order_approver.md) - One row = one approver assigned to a sale order revision from source table `crm_sale_order_approver`, unique on (sale_order_approver_id).
* [crm_sale_order_attachment](crm_sale_order_attachment.md) - One row = one file attached to a sale order from source table `crm_sale_order_attachment`, unique on (sale_order_attachment_id).
* [crm_sale_order_delivery](crm_sale_order_delivery.md) - One row = one delivery round of a sale order from source table `crm_sale_order_delivery`, unique on (sale_order_delivery_id).
* [crm_sale_order_delivery_line](crm_sale_order_delivery_line.md) - One row = one product line within a delivery round from source table `crm_sale_order_delivery_line`, unique on (sale_order_delivery_line_id).
* [crm_sale_order_deposit](crm_sale_order_deposit.md) - One row = one deposit installment of a sale order from source table `crm_sale_order_deposit`, unique on (sale_order_deposit_id).
* [crm_sale_order_line](crm_sale_order_line.md) - One row = one sale order line from source table `crm_sale_order_line`, unique on (sale_order_line_id).
* [crm_sale_order_payment](crm_sale_order_payment.md) - One row = one payment plan of a sale order from source table `crm_sale_order_payment`, unique on (sale_order_payment_id).
* [crm_sale_order_payment_allocation](crm_sale_order_payment_allocation.md) - One row = one allocation of a payment receipt to a deposit installment from source table `crm_sale_order_payment_allocation`, unique on (sale_order_payment_allocation_id).
* [crm_sale_order_payment_receipt](crm_sale_order_payment_receipt.md) - One row = one payment received for a sale order from source table `crm_sale_order_payment_receipt`, unique on (sale_order_payment_receipt_id).
* [crm_sale_order_revision](crm_sale_order_revision.md) - One row = one saved revision of a sale order from source table `crm_sale_order_revision`, unique on (sale_order_revision_id).
* [crm_sale_order_sales_person](crm_sale_order_sales_person.md) - One row = one salesperson assigned to a sale order from source table `crm_sale_order_sales_person`, unique on (sale_order_sales_person_id).
* [crm_sale_order_status_history](crm_sale_order_status_history.md) - One row = one status change or action on a sale order from source table `crm_sale_order_status_history`, unique on (sale_order_status_history_id).
* [inventory_formula_line](inventory_formula_line.md) - One row = one line of a production formula from source table `inventory_formula_line`, unique on (formula_line_id).
* [inventory_formula_versions](inventory_formula_versions.md) - One row = one product formula version from source table `inventory_formula_versions`, unique on (formula_versions_id).
* [inventory_item_price](inventory_item_price.md) - One row = one item price record per item, site and effective date from source table `inventory_item_price`, unique on (inventory_item_price_id).
* [inventory_movement_journal_entries](inventory_movement_journal_entries.md) - One row = one inventory movement journal line (latest version per journal number and line) from source table `inventory_movement_journal_entries`, unique on (journal_number, line_number).
* [inventory_movement_journal_headers](inventory_movement_journal_headers.md) - One row = one inventory movement journal header (latest version per journal number) from source table `inventory_movement_journal_headers`, unique on (journal_number).
* [sales_channel_master_sales_channel](sales_channel_master_sales_channel.md) - One row = one sales channel node from source table `sales_channel_master_sales_channel`, unique on (master_sales_channel_id).
* [sales_customer_sales_territory](sales_customer_sales_territory.md) - One row = one assignment of a customer to a salesperson or sales territory from source table `sales_customer_sales_territory`, unique on (customer_sales_territory_id).
* [sales_employee](sales_employee.md) - One row = one employee from source table `sales_employee`, unique on (employee_id).
* [sales_employee_sale_territory](sales_employee_sale_territory.md) - One row = one assignment of an employee to a sales territory from source table `sales_employee_sale_territory`, unique on (employee_sale_territory_id).
* [sales_sales_territory](sales_sales_territory.md) - One row = one sales territory node from source table `sales_sales_territory`, unique on (sale_territory_id).
* [sync_mac5_inventory_item_price](sync_mac5_inventory_item_price.md) - One row = one synchronized item-price record from source table `sync_mac5_inventory_item_price`, unique on (inventory_item_price_id).

---
type: BigQuery Table
title: "dim_company"
description: "One row = one MAC5 company (ag01, aa05, ab01, ac02, ak02) with its code, Thai and English names and a stable surrogate key."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_company&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_company
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_company.sqlx"
    title: "Dataform definition (dimension/dim_company.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-09T14:42:02+07:00" }
status: draft
---

# What it is

Root company dimension. Other dimensions, facts and views carry `CompanySK` from this table; MAC5 keys are unique only within a company. Master data comes from the externally loaded `mds_dataset.mds_data_company_master`.

Read by: [dim_aging](/dimension/dim_aging.md), [dim_aging_rang](/dimension/dim_aging_rang.md), [dim_avg_collection_score](/dimension/dim_avg_collection_score.md), [dim_bounce_cheque_score](/dimension/dim_bounce_cheque_score.md), [dim_change_district](/dimension/dim_change_district.md), [dim_channel](/dimension/dim_channel.md), [dim_channel_cost](/dimension/dim_channel_cost.md), [dim_channel_finance](/dimension/dim_channel_finance.md), [dim_channel_sales](/dimension/dim_channel_sales.md), [dim_collection_status](/dimension/dim_collection_status.md), [dim_contact_score](/dimension/dim_contact_score.md), [dim_cost_group](/dimension/dim_cost_group.md), [dim_cost_stk](/dimension/dim_cost_stk.md), [dim_customer](/dimension/dim_customer.md), [dim_customer_report_info](/dimension/dim_customer_report_info.md), [dim_customer_segment](/dimension/dim_customer_segment.md), [dim_delivery](/dimension/dim_delivery.md), [dim_department](/dimension/dim_department.md), [dim_department_last](/dimension/dim_department_last.md), [dim_director](/dimension/dim_director.md), [dim_director_last](/dimension/dim_director_last.md), [dim_doctype](/dimension/dim_doctype.md), [dim_grade](/dimension/dim_grade.md), [dim_guarantee](/dimension/dim_guarantee.md), [dim_invoice](/dimension/dim_invoice.md), [dim_order](/dimension/dim_order.md), [dim_payment](/dimension/dim_payment.md), [dim_payment_receive_score](/dimension/dim_payment_receive_score.md), [dim_price](/dimension/dim_price.md), [dim_product_master](/dimension/dim_product_master.md), [dim_product_master_fc](/dimension/dim_product_master_fc.md), [dim_product_mkt](/dimension/dim_product_mkt.md), [dim_product_mkt_director](/dimension/dim_product_mkt_director.md), [dim_project](/dimension/dim_project.md), [dim_quotation](/dimension/dim_quotation.md), [dim_rate_target](/dimension/dim_rate_target.md), [dim_rebate](/dimension/dim_rebate.md), [dim_region](/dimension/dim_region.md), [dim_region_last](/dimension/dim_region_last.md), [dim_region_manager](/dimension/dim_region_manager.md), [dim_region_manager_last](/dimension/dim_region_manager_last.md), [dim_report](/dimension/dim_report.md), [dim_sale_representative](/dimension/dim_sale_representative.md), [dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dim_section](/dimension/dim_section.md), [dim_section_last](/dimension/dim_section_last.md), [dim_section_manager](/dimension/dim_section_manager.md), [dim_section_manager_last](/dimension/dim_section_manager_last.md), [dim_stk_mkt](/dimension/dim_stk_mkt.md), [dim_store](/dimension/dim_store.md), [dim_target_product_group](/dimension/dim_target_product_group.md), [dim_waterpac](/dimension/dim_waterpac.md), [dim_weight_score](/dimension/dim_weight_score.md), [fact_backlog_store](/fact/fact_backlog_store.md), [fact_chq](/fact/fact_chq.md), [fact_delivery](/fact/fact_delivery.md), [fact_invoice](/fact/fact_invoice.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_mir_rs](/fact/fact_mir_rs.md), [fact_mir_vs](/fact/fact_mir_vs.md), [fact_order](/fact/fact_order.md), [fact_order_store](/fact/fact_order_store.md), [fact_quotation](/fact/fact_quotation.md), [fact_transaction_delivery](/fact/fact_transaction_delivery.md), [org_center_unit](/org_center/org_center_unit.md), [rls_ta_customer](/process/rls_ta_customer.md), [view_dim_company](/view/dimension_view/view_dim_company.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [Product_Attribute](/view/onetime/Product_Attribute.md), [Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md), [export_company_source](/view/pub_sub/export_company_source.md).

# Grain and key

One row = one company. `CompanySK` retains the legacy identity: match by `MdsId` first, then fall back to (`CompanyID`, `CompanyCode`). A CompanyCode edit with the same MdsId retains CompanySK. New rows are allocated after the current maximum; rows absent from the complete active MDS source are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | Stable surrogate key retained by the legacy MdsId-first lookup, with CompanyID/CompanyCode fallback; new keys are allocated after the current maximum. |
| `CompanyID` | STRING | MAC5 company id such as ag01, aa05, ab01, ac02, ak02; matches `company_id` in validated/curated MAC5 tables. Part of the natural key. |
| `CompanyCode` | STRING | Short company code from MDS (`CompanyCode`): TM = ag01, TE = ac02, IM = ab01, SHANTA = aa05, SWAS = ak02; second part of the natural key. |
| `CompanyNameTH` | STRING | Company name in Thai (MDS `CompanyNameTH`). |
| `CompanyNameEN` | STRING | Company name in English (MDS `CompanyNameEN`). |
| `MdsId` | STRING | `id` of the source row in `mds_dataset.mds_data_company_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_company.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`); the operation owns this table.
- Reads: `mds_dataset.mds_data_company_master` (master data loaded outside this repo).
- The legacy MdsId-first lookup and CompanyID/CompanyCode fallback run over the complete active MDS source. MERGE matches on CompanySK, updates CompanyNameTH, CompanyNameEN and MdsId, inserts new companies, and hard-deletes companies absent from that source. CompanyID and CompanyCode remain the stored legacy values on matched rows.
# Examples

Company SK for each MAC5 company id.

```sql
SELECT CompanySK, CompanyID, CompanyCode, CompanyNameEN
FROM `databuffet-nonprd.dimension_table.dim_company`
ORDER BY CompanyID;
```

Typical join from a dimension that carries `CompanySK`.

```sql
SELECT c.CompanyID, COUNT(*) AS customers
FROM `databuffet-nonprd.dimension_table.dim_customer` AS cu
JOIN `databuffet-nonprd.dimension_table.dim_company` AS c USING (CompanySK)
GROUP BY c.CompanyID;
```

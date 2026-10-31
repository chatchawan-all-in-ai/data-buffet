---
type: BigQuery View
title: "view_dim_invoice"
description: "One row = one invoice-type document line group (InvoiceSK: IS/BS/AS/QS document x customer x linked order) with order/aging SKs, SCG flag and a resolved customer report (shop) name."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_invoice&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_invoice
tags: ["view", "dimension_view", "mac5", "mds"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_invoice.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_invoice.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Invoice dimension for the transaction model: [dim_invoice](/dimension/dim_invoice.md) enriched with `AgingSK` (from dim_aging by invoice number), `RefOrder` (the order the invoice came from, for BS/AS via the original IS), `FlagSCG`, the shop name for chain customers (`CRCShopName`), the branch name `mecdesc` and the final `CustomerReportName`. `CustomerReportName` is resolved in priority order: MDS nickname, then rule-based names (SCG/Global House/HomePro shops from `mihNotes` or `mecdesc`), then the customer name, always passed through the MDS CRC shop rename. Used by [fact_invoice](/fact/fact_invoice.md), [fact_transcation](/fact/fact_transcation.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md) and [dim_customer_report_info](/dimension/dim_customer_report_info.md).

# Grain and key

One row per `InvoiceSK` (QUALIFY ROW_NUMBER over InvoiceSK ordered by AgingSK). dim_invoice natural key: company + year/month/day + vnos + customer + milLinkVcno.

# Schema

| Column | Type | Description |
|---|---|---|
| `OrderSK` | INT64 | SK of the order in dim_order: the invoice's own OrderSK, else the latest OrderSK matching `RefOrder` + CompanySK for BS/AS documents. |
| `AgingSK` | INT64 | SK of the invoice in dim_aging, joined on invoice number (`CFSvnosID = mihvnos`) and CompanySK; NULL when not in aging. Regenerated nightly. |
| `InvoiceSK` | INT64 | Stable SK of the invoice row in dim_invoice (MERGE). |
| `mix_date` | DATE | Document date, `PARSE_DATE('%Y%m%d', CONCAT(mihYear, mihMonth, mihDay))`. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `mihDay` | INT64 | Day of the document date (MAC5 mih). |
| `mihMonth` | INT64 | Month of the document date. |
| `mihYear` | INT64 | Year of the document date. |
| `mihType` | STRING | MAC5 document type code (e.g. IS invoice, BS credit note, AS debit note, QS quotation, PS order). |
| `mihCus` | STRING | Customer code (`debcode`) on the document. |
| `mihVnos` | STRING | Document number (vnos). |
| `mihPer` | STRING | Salesperson code on the document. |
| `pernamet` | STRING | Salesperson name from the MAC5 `per` table (personal data). |
| `per_sale1` | FLOAT64 | Sales share (%) of the first salesperson parsed from MAC5 mih2 `mih2perpc`; 100 when the invoice is not split. |
| `mih2per2` | STRING | Code of the second salesperson on a split invoice (mih2per2); '0' when not split. |
| `per_sale2` | FLOAT64 | Sales share (%) of the second salesperson; 0 when not split. |
| `mihStatus` | INT64 | Status code of the document (joined to ar_s/ap_s for the name). |
| `StatusDesc` | STRING | Status name from MAC5 ar_s (sales document types) or ap_s (purchase types). |
| `mihCancel` | INT64 | Cancel flag (-1 = cancelled in MAC5, 0 = active). Cancelled invoices can survive dim_invoice branches and this view does not filter them. |
| `mihRef1` | STRING | Reference 1 on the document (for invoices, the order number it references). |
| `mihRef2` | STRING | Reference 2 on the document. |
| `mihDep` | STRING | Department code on the document (join to channel DepCode). |
| `mihJob` | STRING | Job code on the document. |
| `InvoiceSalesFlag` | STRING | 'Yes' when the invoice is split between salespeople (per_sale1 <> 100), else 'No'. |
| `milLinkVcno` | STRING | Linked document number from the invoice lines (curated_mil `milLinkVcno`); for IS this is the source order number. |
| `mihNotes` | STRING | Free-text notes on the document. |
| `mihDesc` | STRING | Description text on the document. |
| `mihMec` | STRING | Branch (mec) code on the document; joined to mec for `mecdesc`. |
| `RefOrder` | STRING | Order number the invoice came from: `milLinkVcno` of the invoice, or for BS/AS the `milLinkVcno` of the original IS invoice it links to. |
| `FlagSCG` | STRING | Result of `fn_flag_scg(RefOrder, mihCus)`: marks SCG-related invoices; NULL otherwise (function definition is in function_dataset). |
| `CRCShopName` | STRING | Shop name for chain customers (SCG, Siam Global House, HomePro pattern), extracted from `mihNotes` by `#D/S`-style patterns, after the MDS CRC rename; NULL for other customers. |
| `mecdesc` | STRING | Branch name from `mec.mecdesc` (joined by company + `mihMec = meccode`). |
| `CustomerReportName` | STRING | Final shop name for reports: MDS nickname if set, else rule-based name (branch name for SCG/GB/HomePro, CRC shop name, or cleaned customer name), then MDS CRC rename applied. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_invoice.sqlx` (`type: "view"`, tags `view`).
- Reads: `function_dataset.fn_get_scg_customer_ids` (UDF), [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), `function_dataset.clean_company_prefix` (UDF), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_aging](/dimension/dim_aging.md), `function_dataset.fn_flag_scg` (UDF), [dimension_table.dim_order](/dimension/dim_order.md), [validated_mac5.mec](/validated/validated_mac5/mec.md), `mds_dataset.mds_data_crc_shop_name_rename` (master data loaded outside this repo).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_invoice, dim_aging, view_dim_customer, dim_order, mec (validated_mac5), MDS CRC shop rename; uses UDFs `fn_flag_scg`, an SCG customer-id list function and `clean_company_prefix` (all in function_dataset). dim_invoice is MERGE with stable SK; the view is deployed after dim_aging, dim_order, mec and view_dim_customer exist.

# Examples

Invoices with their report shop name for one month:

```sql
SELECT InvoiceSK, mihVnos, mihType, CustomerReportName, FlagSCG
FROM `databuffet-nonprd.dimension_view.view_dim_invoice`
WHERE companyID = 'ag01' AND mix_date BETWEEN '2026-10-01' AND '2026-10-31'
```

Invoice counts by type:

```sql
SELECT mihType, COUNT(*) AS invoices
FROM `databuffet-nonprd.dimension_view.view_dim_invoice`
WHERE mix_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 30 DAY)
GROUP BY mihType
```

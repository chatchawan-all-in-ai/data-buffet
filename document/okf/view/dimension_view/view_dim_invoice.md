---
type: BigQuery View
title: "view_dim_invoice"
description: "One row = one `dim_invoice` sales document with each matching customer and name record, with order/aging SKs, SCG flag and a resolved shop name; `InvoiceSK` can repeat."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

Invoice dimension for the transaction model: [dim_invoice](/dimension/dim_invoice.md) enriched with `AgingSK` (from dim_aging by invoice number), `RefOrder` (the order the invoice came from, for BS/AS via the original IS), `FlagSCG`, the shop name for chain customers (`CRCShopName`), the branch name `mecdesc` and the final `CustomerReportName`. `CustomerReportName` is resolved in priority order: the MDS nickname when `FlagMDSNickName` is true (used as is); otherwise the rule-based name (SCG/Global House/HomePro shops: branch name `mecdesc`, else the CRC shop name from `mihNotes`, else the cleaned customer name) passed through the MDS CRC shop rename. For the Siam Global House customer the rule-based name has a trailing " จ.<province>" removed and the mall-name prefix normalised to "สยามโกลบอลเฮ้าส์ ".

Read by: [dim_customer_report_info](/dimension/dim_customer_report_info.md), [export_view_dim_invoice](/view/pub_sub/export_view_dim_invoice.md), [fact_invoice](/fact/fact_invoice.md), [fact_transcation](/fact/fact_transcation.md) and [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one `dim_invoice` sales document with each combination of matching customer and name records: intended key `InvoiceSK` (not guaranteed unique). `tab_main` keeps one row per `InvoiceSK` with `QUALIFY ROW_NUMBER()` ordered by `AgingSK`; subsequent LEFT JOINs to [view_dim_customer](/view/dimension_view/view_dim_customer.md#grain-and-key), `mec` and the active MDS CRC rename rows can add rows, with no final deduplication. dim_invoice natural key: company + year/month/day + vnos + customer + milLinkVcno.

# Schema

| Column | Type | Description |
|---|---|---|
| `OrderSK` | INT64 | SK of the order in dim_order: the invoice's own OrderSK, else the latest OrderSK matching `RefOrder` + CompanySK for BS/AS documents. |
| `AgingSK` | INT64 | SK of the invoice in dim_aging, joined on invoice number (`CFSvnosID = mihvnos`) and CompanySK; NULL when not in aging. Regenerated nightly. |
| `InvoiceSK` | INT64 | Stable SK of the invoice row in dim_invoice (MERGE). |
| `mix_date` | DATE | Document date, `PARSE_DATE('%Y%m%d', CONCAT(mihYear, mihMonth, mihDay))`. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `mihDay` | INT64 | Day part of the document date. |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihType` | STRING | Document type code (`IS` = invoice, `AS` = debit note, `BS` = credit note, `QS` = sales quotation). |
| `mihCus` | STRING | Customer code, matching `deb.debcode`. |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `mihPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `pernamet` | STRING | Employee name in Thai (first name, surname and nickname in parentheses). |
| `per_sale1` | FLOAT64 | Sales share (%) of the first salesperson parsed from MAC5 mih2 `mih2perpc`; 100 when the invoice is not split. |
| `mih2per2` | STRING | Code of the second salesperson on a split invoice (mih2per2); '0' when not split. |
| `per_sale2` | FLOAT64 | Sales share (%) of the second salesperson; 0 when not split. |
| `mihStatus` | INT64 | Document status code from the header, with sales status meanings in `ar_s`. |
| `StatusDesc` | STRING | Status name from MAC5 `ar_s` for the sales document type. |
| `mihCancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihRef1` | STRING | Reference document number 1 for the source quotation or sales order. |
| `mihRef2` | STRING | Customer purchase-order or external order reference number. |
| `mihDep` | STRING | Department code of the document, used as the sales channel code. |
| `mihJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `InvoiceSalesFlag` | STRING | 'Yes' when the invoice is split between salespeople (per_sale1 <> 100), else 'No'. |
| `milLinkVcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `mihNotes` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihDesc` | STRING | Free-text document description. |
| `mihMec` | STRING | Memo-card code of the document, matching `mec.meccode` (holds the shop or branch name for chain-store customers). |
| `RefOrder` | STRING | Order number the invoice came from: `milLinkVcno` of the invoice, or for BS/AS the `milLinkVcno` of the original IS invoice it links to. |
| `FlagSCG` | STRING | Result of `fn_flag_scg(RefOrder, mihCus)`: marks SCG-related invoices; NULL otherwise (function definition is in function_dataset). |
| `CRCShopName` | STRING | Shop name for chain customers (SCG, Siam Global House, HomePro pattern), extracted from `mihNotes` by `#D/S`-style patterns, after the MDS CRC rename; NULL for other customers. |
| `mecdesc` | STRING | Card title, used as the shop or branch name of chain-store customers in invoice reporting. |
| `CustomerReportName` | STRING | Final shop name for reports: the MDS nickname when `FlagMDSNickName` is true, else the rule-based name (branch name for SCG/GB/HomePro, CRC shop name, or cleaned customer name) passed through the MDS CRC rename; for the Siam Global House customer the trailing " จ.<province>" is removed and the mall-name prefix normalised. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_invoice.sqlx` (`type: "view"`, tags `view`).
- Reads: `function_dataset.fn_get_scg_customer_ids` (UDF), [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), `function_dataset.clean_company_prefix` (UDF), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_aging](/dimension/dim_aging.md), `function_dataset.fn_flag_scg` (UDF), [dimension_table.dim_order](/dimension/dim_order.md), [validated_mac5.mec](/validated/validated_mac5/mec.md), `mds_dataset.mds_data_crc_shop_name_rename` (master data loaded outside this repo).

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

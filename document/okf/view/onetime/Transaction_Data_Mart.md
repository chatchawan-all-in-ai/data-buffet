---
type: BigQuery View
title: "Transaction_Data_Mart"
description: "One row = one line (curated_mil) of an invoice, debit note, credit note or QS document (types IS/AS/BS/QS) per company, with header fields, VAT allocation and address SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=onetime&t=Transaction_Data_Mart&page=table"
tags: ["view", "onetime", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/onetime/Transaction_Data_Mart.sqlx"
    title: "Dataform definition (view/onetime/Transaction_Data_Mart.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The sales-line data mart that feeds the physical table [fact_transcation](/fact/fact_transcation.md). It joins MAC5 document headers ([curated_mih](/curated/curated_mac5/curated_mih.md)) to their lines ([curated_mil](/curated/curated_mac5/curated_mil.md)) for document types IS/AS/BS/QS, adds stock attributes (stock group, barcode, VAT rate), the quotation reached through the linked order, the customer's address SKs, and allocates the document VAT and deposit to each line so VAT-inclusive amounts can be reported. It has no org/channel/product SKs yet; those are added by `fact_transcation` and `view_fact_transcation`.

Used by [fact_table.fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per `curated_mil` line of a document of type IS, AS, BS or QS: key (company, milType, milVnos, milCus, milListno, plus split-sale `milPer` for ag01). It uses an INNER JOIN of `curated_mih` to `curated_mil` on year/month/day/type/number/customer/company, so documents without lines are absent; the LEFT JOINs (quotation, stk, address, company) are intended to stay 1:1 (`stk` is `SELECT DISTINCT`).

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | SK of `dim_company` (join on `company_id`); stable. |
| `companyID` | STRING | Company code (ag01/aa05/ab01/ac02/ak02) from `dim_company`. |
| `mihvatno` | STRING | VAT tax-invoice number of the document header (`curated_mih.mihvatno`). |
| `mihdesc` | STRING | Header description text of the document (`curated_mih.mihdesc`). |
| `mihmemo` | STRING | Header memo text (`curated_mih.mihmemo`). |
| `memoextract` | STRING | Payment code extracted from the memo; joins to `dim_payment.CodeMemo` to give `PaymentSK` (`curated_mih.memoextract`). |
| `mihmemonew` | STRING | Cleaned/new-format header memo (`curated_mih.mihmemonew`). |
| `mihCancel` | INT64 | Document cancel flag (`-1` = cancelled, 0 = active; NULL treated as not cancelled). |
| `mihStatus` | INT64 | Document status code (`curated_mih.mihstatus`); 32 and 33 are treated as excluded by `fn_flag_exc`. |
| `mihnotes` | STRING | Header notes (`curated_mih.mihnotes`). |
| `QuotationID` | INT64 | Quotation id (`curated_tbook_quotation.id`) reached through the linked PS (order) document: `milLinkvcno -> PS mihVnos -> mihref1 = quotation running`. |
| `QuotationCode` | STRING | Quotation running number (`curated_tbook_quotation.running`) found the same way. |
| `milDay` | INT64 | Day of the bill date. |
| `milMonth` | INT64 | Month of the bill date. |
| `milYear` | INT64 | Year of the bill date. |
| `milType` | STRING | MAC5 document type: `IS` invoice, `AS` debit note, `BS` credit note, `QS` is also included by the source filter `mihtype IN ('IS','AS','BS','QS')` (its meaning is not documented in the repo). |
| `milVnos` | STRING | Document number (`milVnos`); with `milType`, `milCus` and `milListno` it identifies the line. NULL on the zero-filled calendar rows of `view_fact_transcation`. |
| `milCus` | STRING | Customer code on the document; matches `dim_customer.debcode` / `validated_mac5.deb.debcode`. |
| `milStk` | STRING | MAC5 product (stock) code; matched case-insensitively to `dim_product_master.ProductCode` and `dim_stk_mkt.StkCode`. |
| `milJob` | STRING | Job code of the line (MAC5 `milJob`). |
| `milDep` | STRING | Department code of the line (MAC5 `milDep`); joins to `view_dim_channel.DepCode` (`ChannelSK`) and is used by the sale-rep matching rules. |
| `milPer` | STRING | Sales-person code of the line. For ag01 documents with split-sale this is already the share-owner (curated_mil duplicates the line per person). |
| `milPer_raw` | STRING | Sales-person code before the split-sale rewrite (`curated_mil.milPer_raw`). |
| `milDoc` | STRING | Pass-through of MAC5 `mil.milDoc`; meaning not documented in the repo |
| `milMec` | STRING | Pass-through of MAC5 `mil.milMec`; meaning not documented in the repo |
| `milSto` | STRING | Pass-through of MAC5 `mil.milSto`; meaning not documented in the repo |
| `milStomt` | STRING | Pass-through of MAC5 `mil.milStomt`; meaning not documented in the repo |
| `milListno` | INT64 | Line number inside the document. |
| `milQuan` | FLOAT64 | Quantity of the line after split-sale division. |
| `milQuan_raw` | FLOAT64 | Quantity before the split-sale division (full line quantity). |
| `milQuanp2` | FLOAT64 | Pass-through of MAC5 `mil.milQuanp2`; meaning not documented in the repo |
| `milAdisc` | FLOAT64 | Additional/line discount amount from MAC5 (`milAdisc`, after split-sale); not documented further in the repo. |
| `milAdisc_raw` | FLOAT64 | `milAdisc` before the split-sale division. |
| `milCog` | FLOAT64 | Gross line amount excluding VAT (`milCog`; surfaced as `GrossAmountExcVat` in `Model_Invoice_Transaction`). |
| `milCog_raw` | FLOAT64 | `milCog` before the split-sale division. |
| `milConv` | FLOAT64 | Unit conversion factor of the line (inferred from the name). |
| `milDisca` | FLOAT64 | Discount amount of the line excluding VAT (`DiscountAmountExcVat` in `Model_Invoice_Transaction`). |
| `milDisca_raw` | FLOAT64 | Discount amount before the split-sale division. |
| `milDisct` | STRING | Discount text/expression of the line as entered in MAC5 (inferred from the name). |
| `milVat` | FLOAT64 | VAT figure carried on the MAC5 line (`milVat`); the allocated document VAT is the separate `Vat` column. |
| `milVat_raw` | FLOAT64 | `milVat` before the split-sale division. |
| `milSum` | FLOAT64 | Net line amount excluding VAT (`NetSalesExcVat`). |
| `milSum_raw` | FLOAT64 | Line amount excluding VAT before the split-sale division. |
| `milCut` | INT64 | Boolean-like flag of the line (only -1/0 values, not a delivered quantity). |
| `milStype` | INT64 | Line type code (`milstype`); code list not documented in the repo. |
| `milUname` | STRING | Unit-of-measure name of the line (`milUname`, inferred from the name). |
| `milDesc` | STRING | Line description text. |
| `milVcol1` | STRING | Pass-through of MAC5 `mil.milVcol1`; meaning not documented in the repo |
| `milVcol2` | STRING | Pass-through of MAC5 `mil.milVcol2`; meaning not documented in the repo |
| `milVcol3` | STRING | Pass-through of MAC5 `mil.milVcol3`; meaning not documented in the repo |
| `milVcol4` | STRING | Pass-through of MAC5 `mil.milVcol4`; meaning not documented in the repo |
| `milCurc` | INT64 | Currency code of the line. |
| `milExchg` | FLOAT64 | Exchange rate of the line. |
| `milAcost` | FLOAT64 | Pass-through of MAC5 `mil.milAcost`; meaning not documented in the repo |
| `milPqm` | INT64 | Pass-through of MAC5 `mil.milPqm`; meaning not documented in the repo |
| `milPmfrom` | INT64 | Pass-through of MAC5 `mil.milPmfrom`; meaning not documented in the repo |
| `milPmto` | INT64 | Pass-through of MAC5 `mil.milPmto`; meaning not documented in the repo |
| `milTag` | INT64 | Pass-through of MAC5 `mil.milTag`; meaning not documented in the repo |
| `milLinkvcno` | STRING | Number of the linked document (e.g. the order PS document for an invoice, or the invoice for a note); used to find orders/quotations and by `fn_flag_scg`. |
| `milLinkvcdate` | DATETIME | Date of the linked document. |
| `milLinkvctype` | STRING | Type of the linked document. |
| `milLinkvcdeposit` | STRING | Pass-through of MAC5 `mil.milLinkvcdeposit`; meaning not documented in the repo |
| `milLinkvcid` | INT64 | Pass-through of MAC5 `mil.milLinkvcid`; meaning not documented in the repo |
| `milClearum` | INT64 | Pass-through of MAC5 `mil.milClearum`; meaning not documented in the repo |
| `milExpdate` | DATETIME | Expiry date on the line (inferred from the name). |
| `milNotes` | STRING | Line notes. |
| `milNotkl` | INT64 | Pass-through of MAC5 `mil.milNotkl`; meaning not documented in the repo |
| `milDelvdt` | DATETIME | Delivery date of the line (inferred from the name). |
| `milDatesp` | DATETIME | Pass-through of MAC5 `mil.milDatesp`; meaning not documented in the repo |
| `milNumcsp` | FLOAT64 | Pass-through of MAC5 `mil.milNumcsp`; meaning not documented in the repo |
| `milNumisp` | INT64 | Pass-through of MAC5 `mil.milNumisp`; meaning not documented in the repo |
| `milCost` | FLOAT64 | Cost amount of the line (MAC5 `milCost`, inferred from the name). |
| `milUcost` | FLOAT64 | Unit cost (inferred from the name). |
| `milUprice` | FLOAT64 | Unit price (inferred from the name). |
| `milUsequanp` | INT64 | Pass-through of MAC5 `mil.milUsequanp`; meaning not documented in the repo |
| `milVcol5` | STRING | Pass-through of MAC5 `mil.milVcol5`; meaning not documented in the repo |
| `milFitem` | INT64 | Pass-through of MAC5 `mil.milFitem`; meaning not documented in the repo |
| `asatdate` | DATE | Load date (ASATDATE) of the source `curated_mil` row; not a business date. |
| `percent_sale` | STRING | Split-sale share of this line as text (e.g. `60.00%`); `100.00%` when the line is not split (only ag01 splits lines between two sales people). |
| `stkGroup` | STRING | MAC5 stock group of the product (`validated_mac5.stk.stkgroup`). |
| `OrderProvinceSK` | INT64 | Province SK of the customer's address (`view_deb_address_data`, AI-parsed from the debtor address), used for order-based rules. |
| `OrderDistrictSK` | INT64 | District SK of the customer's address. |
| `OrderSubDistrictSK` | INT64 | Sub-district SK of the customer's address. |
| `Vat` | FLOAT64 | VAT of the document allocated to the line: `milSum / SUM(milSum over document) * mihVatsum` (sign flipped for `BS` credit notes); 0 when the document total is 0. |
| `milsum_incvat` | FLOAT64 | Net amount including VAT: `milSum + Vat`. |
| `mildisca_incvat` | FLOAT64 | Discount amount including VAT: `milDisca * stkVat` when the document carries VAT (`mihVatsum <> 0`), else `milDisca`. |
| `milcog_incvat` | FLOAT64 | Gross amount including VAT: `milCog * stkVat` when the document carries VAT, else `milCog`. |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`). |
| `DepositExcVat` | FLOAT64 | Share of the document's extra/deposit amount (`mihExtrasum`) allocated to this line by `milSum` weight, excluding VAT. |
| `DepositIncVat` | FLOAT64 | Allocated deposit including VAT (`mihExtrasum` + `mihExtravat` shares). |
| `DepositVat` | FLOAT64 | VAT part of the allocated deposit. |

# How it is built

- Definition: `definitions/view/onetime/Transaction_Data_Mart.sqlx` (`type: "view"`, tags `view`).
- Reads: [validated_mac5.stk](/validated/validated_mac5/stk.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [curated_mac5.curated_tbook_quotation](/curated/curated_mac5/curated_tbook_quotation.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [process_dataset.view_deb_address_data](/view/process_dataset/view_deb_address_data.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; its inputs `curated_mih`, `curated_mil`, `curated_tbook_quotation` and `validated_mac5.stk` are read via `ref()` (curated/validated tags); `view_deb_address_data` and `dim_company` are declared dependencies. The table `fact_transcation` (tag `fact_daily`) reads this view every night, so changes here only reach reporting after that rebuild. Dataset `onetime` is kept for BI compatibility, not because it is one-off.

# Examples

Line count and net amount per company and document type for the current year.

```sql
SELECT companyID, milType, COUNT(*) AS lines, SUM(milSum) AS net_exc_vat, SUM(milsum_incvat) AS net_inc_vat
FROM `databuffet-nonprd.onetime.Transaction_Data_Mart`
WHERE milYear = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY companyID, milType
ORDER BY companyID, milType
```

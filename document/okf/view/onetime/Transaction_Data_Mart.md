---
type: BigQuery View
title: "Transaction_Data_Mart"
description: "One row = one line (curated_mil) of an invoice, debit note, credit note or QS document (types IS/AS/BS/QS) per company, with header fields, VAT allocation and address SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=onetime&t=Transaction_Data_Mart&page=table"
project_id: databuffet-nonprd
dataset_id: onetime
table_id: Transaction_Data_Mart
tags: ["view", "onetime", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/onetime/Transaction_Data_Mart.sqlx"
    title: "Dataform definition (view/onetime/Transaction_Data_Mart.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The sales-line data mart that feeds the physical table [fact_transcation](/fact/fact_transcation.md). It joins MAC5 document headers ([curated_mih](/curated/curated_mac5/curated_mih.md)) to their lines ([curated_mil](/curated/curated_mac5/curated_mil.md)) for document types IS/AS/BS/QS, adds stock attributes (stock group, barcode, VAT rate), the quotation reached through the linked order, the customer address SKs, and allocates the document VAT and deposit to each line so VAT-inclusive amounts can be reported. It carries no org, channel or product SKs; `fact_transcation` and `view_fact_transcation` add them.

Read by: [fact_transcation](/fact/fact_transcation.md).

# Grain and key
One row = one `curated_mil` line of a document of type IS, AS, BS or QS: key `companyID`, `milType`, `milVnos`, `milCus`, `milListno`, plus `milPer` for split-sale rows. It uses an INNER JOIN of `curated_mih` to `curated_mil` on year/month/day/type/number/customer/company, so documents without lines are absent. The LEFT JOINs add quotation, stock, address and company columns to each line.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | SK of `dim_company` (join on `company_id`); stable. |
| `companyID` | STRING | MAC5 company code from `dim_company`. |
| `mihvatno` | STRING | Tax invoice number of the document. |
| `mihdesc` | STRING | Free-text document description. |
| `mihmemo` | STRING | Free-text document memo with an optional tag enclosed in `฿` signs. |
| `memoextract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `mihmemonew` | STRING | Document memo with the tag enclosed in `฿` signs removed, or NULL when no text remains. |
| `mihCancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihStatus` | INT64 | Document status code from the header, with sales status meanings in `ar_s`. |
| `mihnotes` | STRING | Free-text notes such as delivery instructions or site details. |
| `QuotationID` | INT64 | Quotation id (`curated_tbook_quotation.id`) reached through the linked PS (order) document: `milLinkvcno -> PS mihVnos -> mihref1 = quotation running`. |
| `QuotationCode` | STRING | Quotation running number (`curated_tbook_quotation.running`) found the same way. |
| `milDay` | INT64 | Day part of the document date. |
| `milMonth` | INT64 | Month part of the document date. |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milType` | STRING | Document type code (`IS` = invoice, `AS` = debit note, `BS` = credit note, `QS` = sales quotation). |
| `milVnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milCus` | STRING | Customer code, matching `deb.debcode`. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milJob` | STRING | Job code of the line (sales job or project category such as `TT`, `SHOP`, or a project number). |
| `milDep` | STRING | Department code of the line, used as the sales channel code. |
| `milPer` | STRING | Salesperson code of the line, replaced by the second salesperson's code on the second ag01 split-sale row. |
| `milPer_raw` | STRING | Original salesperson code before the split-sale override. |
| `milDoc` | STRING | Document print-form code of the line from the MAC5 `doc` master. |
| `milMec` | STRING | Memo-card code of the line, matching `mec.meccode`. |
| `milSto` | STRING | Warehouse (store) code the line is issued from, matching `sto` store codes. |
| `milStomt` | STRING | Destination warehouse code for transfer lines. |
| `milListno` | INT64 | Line number within the document. |
| `milQuan` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milQuan_raw` | FLOAT64 | Full line quantity before split-sale allocation, with negative values for BS credit notes. |
| `milQuanp2` | FLOAT64 | Quantity in the secondary unit. |
| `milAdisc` | FLOAT64 | Allocated header discount deducted from the line amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milAdisc_raw` | FLOAT64 | Full allocated header discount before split-sale allocation, with negative values for BS credit notes. |
| `milCog` | FLOAT64 | Gross line amount before discounts excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milCog_raw` | FLOAT64 | Full gross line amount before discounts excluding VAT and before split-sale allocation, with negative values for BS credit notes. |
| `milConv` | FLOAT64 | Unit conversion factor of the line (1 when no conversion). |
| `milDisca` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milDisca_raw` | FLOAT64 | Full line discount amount excluding VAT before split-sale allocation, with negative values for BS credit notes. |
| `milDisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milVat` | FLOAT64 | Line VAT amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milVat_raw` | FLOAT64 | Full line VAT amount before split-sale allocation, with negative values for BS credit notes. |
| `milSum` | FLOAT64 | Net line amount excluding VAT after line and allocated header discounts, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milSum_raw` | FLOAT64 | Full net line amount excluding VAT after line and allocated header discounts and before split-sale allocation, with negative values for BS credit notes. |
| `milCut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `milStype` | INT64 | Line item type (1 = item, 2 = serial-tracked item, 3 = service). |
| `milUname` | STRING | Unit name of the line (e.g. `SET`, `ชุด`, `Pcs.`). |
| `milDesc` | STRING | Free-text line description. |
| `milVcol1` | STRING | User-defined text column 1 of the line. |
| `milVcol2` | STRING | User-defined text column 2 of the line. |
| `milVcol3` | STRING | User-defined text column 3 of the line. |
| `milVcol4` | STRING | User-defined text column 4 of the line. |
| `milCurc` | INT64 | Currency code (0 = Thai baht). |
| `milExchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `milAcost` | FLOAT64 | Average cost of the line. |
| `milPqm` | INT64 | Price-quantity mode of the line. |
| `milPmfrom` | INT64 | Start of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `milPmto` | INT64 | End of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `milTag` | INT64 | Tag marker of the line. |
| `milLinkvcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `milLinkvcdate` | DATETIME | Date of the linked source document. |
| `milLinkvctype` | STRING | Document type of the linked source document (e.g. `PS`, `PP`). |
| `milLinkvcdeposit` | STRING | Deposit amount and VAT deducted from the linked document, stored as `amount/VAT` text. |
| `milLinkvcid` | INT64 | Internal ID of the linked source-document line. |
| `milClearum` | INT64 | Flag: outstanding quantity of the line cleared (0 = still open). |
| `milExpdate` | DATETIME | Expiry date of the line item. |
| `milNotes` | STRING | Free-text line notes. |
| `milNotkl` | INT64 | Flag indicating that the line is excluded from stock reservation. |
| `milDelvdt` | DATETIME | Requested delivery date of the line. |
| `milDatesp` | DATETIME | Special date of the line. |
| `milNumcsp` | FLOAT64 | Special numeric field of the line. |
| `milNumisp` | INT64 | Special integer field of the line. |
| `milCost` | FLOAT64 | Cost amount of the line. |
| `milUcost` | FLOAT64 | Unit cost of the line. |
| `milUprice` | FLOAT64 | Unit price of the line, excluding VAT. |
| `milUsequanp` | INT64 | Flag indicating use of the secondary-unit quantity (1 = yes). |
| `milVcol5` | STRING | User-defined text column 5 of the line. |
| `milFitem` | INT64 | Free-item flag of the line. |
| `asatdate` | DATE | Load date (ASATDATE) of the source `curated_mil` row; not a business date. |
| `percent_sale` | STRING | Split-sale share of this line as text (e.g. `60.00%`); `100.00%` when the line is not split (only ag01 splits lines between two sales people). |
| `stkGroup` | STRING | Stock group code (joins `stg.stgcode`). |
| `OrderProvinceSK` | INT64 | Province SK of the customer's address (`view_deb_address_data`, AI-parsed from the debtor address), used for order-based rules. |
| `OrderDistrictSK` | INT64 | District SK of the customer's address. |
| `OrderSubDistrictSK` | INT64 | Sub-district SK of the customer's address. |
| `Vat` | FLOAT64 | VAT allocated to the line: `milSum / over_milsum * mihVatsum`, where `over_milsum` is `SUM(milSum)` partitioned by `milDay`, `milMonth`, `milYear`, `milType`, `milCus`, `milVnos`; 0 when the window total is NULL or 0. |
| `milsum_incvat` | FLOAT64 | Net amount including VAT: `milSum + Vat`. |
| `mildisca_incvat` | FLOAT64 | Discount amount including VAT: `milDisca * stkVat` when the document carries VAT (`mihVatsum <> 0`), else `milDisca`. |
| `milcog_incvat` | FLOAT64 | Gross amount including VAT: `milCog * stkVat` when the document carries VAT, else `milCog`. |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`). |
| `DepositExcVat` | FLOAT64 | Deposit amount excluding VAT allocated to the line by its share of the document net amount (`milSum / SUM(milSum)` over the same window as `Vat`), or zero when that total is zero. |
| `DepositIncVat` | FLOAT64 | Deposit amount including VAT allocated to the line by its share of the document net amount (`milSum / SUM(milSum)` over the same window as `Vat`), or zero when that total is zero. |
| `DepositVat` | FLOAT64 | Deposit VAT allocated to the line by its share of the document net amount (`milSum / SUM(milSum)` over the same window as `Vat`), or zero when that total is zero. |

# How it is built

- Definition: `definitions/view/onetime/Transaction_Data_Mart.sqlx` (`type: "view"`, tags `view`).
- Reads: [validated_mac5.stk](/validated/validated_mac5/stk.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [curated_mac5.curated_tbook_quotation](/curated/curated_mac5/curated_tbook_quotation.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [process_dataset.view_deb_address_data](/view/process_dataset/view_deb_address_data.md), [dimension_table.dim_company](/dimension/dim_company.md).

# Examples

Line count and net amount per company and document type for the current year.

```sql
SELECT companyID, milType, COUNT(*) AS lines, SUM(milSum) AS net_exc_vat, SUM(milsum_incvat) AS net_inc_vat
FROM `databuffet-nonprd.onetime.Transaction_Data_Mart`
WHERE milYear = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY companyID, milType
ORDER BY companyID, milType
```

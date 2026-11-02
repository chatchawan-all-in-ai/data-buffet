---
type: BigQuery Table
title: "fact_delivery"
description: "One row = the delivery status counts of one invoice item (company, invoice, item, vehicle, delivery date, location) for one matching invoice product candidate; retained product versions repeat the counts and invoice measures."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_delivery
tags: ["fact", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_delivery.sqlx"
    title: "Dataform definition (fact/fact_delivery.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Delivery-tracking fact built from the MAC5 trip tables (`ttrip_document`, `ttrip`, `tdelivery`) for IS invoices that link to orders, showing for each invoice item the vehicle, delivery date, GPS point/zone and how many units are in each status (loaded on truck or not, vehicle released or not, shipment not yet delivered / received / refused by customer). It is enriched with [dim_delivery](/dimension/dim_delivery.md) and the invoice quantities from [fact_transaction_delivery](/fact/fact_transaction_delivery.md). It answers where deliveries stand and whether customers accepted the goods. No other table reads it.

Used by / context: used by nothing else in the repo.

# Grain and key

One row per `FactDeliverySK` (ROW_NUMBER over CompanySK, documentID, DeliveryDate, item). Business grain: company + documentID (invoice number) + item + vehicle + DeliveryDate + location. Items come from `ttrip_document.fitem`; if (document, trip code, item) is not matched to `curated_mil`, the alternate item `fitem2` is used. The status aggregation initially has that business grain, but the later join to fact_transaction_delivery emits every matching invoice/ProductSK candidate. Retained barcode versions therefore repeat all status counts and totalItems as well as invoice measures; FactDeliverySK identifies an expanded row. Only items present in `curated_mil` for the same document (case-insensitive) are kept; items starting with '8' are excluded; documents are restricted to IS lines with a link number.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactDeliverySK` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, documentID, DeliveryDate, item. Regenerates every run. |
| `DeliverySK` | INT64 | Surrogate key of [dim_delivery](/dimension/dim_delivery.md) (join `documentID`, company); NULL if unmatched. |
| `FactTransDeliverySK` | INT64 | [fact_transaction_delivery](/fact/fact_transaction_delivery.md).FactTransDeliverySK of the invoice line (join documentID = milvnos, case-insensitive item); NULL if unmatched. |
| `InvoiceSK` | INT64 | InvoiceSK carried from fact_transaction_delivery. |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code. |
| `documentID` | STRING | Invoice document number (`ttrip_document.fdocument`). |
| `Vehicle` | STRING | Vehicle identifier of the trip (`ttrip.fvehicle`). |
| `DeliveryDate` | DATE | Date part (first 8 digits yyyymmdd) of `ttrip_document.fdatetime`. |
| `Lattitude` | STRING | Delivery latitude from `tdelivery.flattitude` (STRING; spelling as in the source). |
| `Longtitude` | STRING | Delivery longitude from `tdelivery.flongtitude` (STRING). |
| `Zone` | STRING | Delivery zone from `tdelivery.fzone`. |
| `Point` | STRING | Delivery point-of-interest from `tdelivery.fpoi`. |
| `item` | STRING | Product code of the delivered item: `fitem`, or `fitem2` when `fitem` is not matched to the invoice. |
| `documentStatus_1` | INT64 | Count of records loaded on the truck (`fdocument` populated; Thai label 'จัดของขึ้นรถ'). |
| `documentStatus_2` | INT64 | Count of records not yet loaded ('ยังไม่จัดของ'). |
| `deliveryStatus_1` | INT64 | Count of records whose vehicle was released (`ttrip.fpass_Date` present; 'ปล่อยรถแล้ว'). |
| `deliveryStatus_2` | INT64 | Count of records whose vehicle was not released ('ไม่ปล่อยรถ'). |
| `shipmentStatus_1` | INT64 | Count of records not yet delivered (no `fserial_no` in tdelivery; 'ยังไม่ส่งของ'). |
| `shipmentStatus_2` | INT64 | Count of records received by the customer ('รับสินค้าแล้ว': delivered and `fcancel = '0'`). |
| `shipmentStatus_3` | INT64 | Count of records refused by the customer ('ลูกค้าไม่รับ': delivered with `fcancel` not '0'). |
| `totalItems` | INT64 | Total number of trip-document item records (sum of `qty2`) behind the row. |
| `ProductSK` | INT64 | Product SK carried from fact_transaction_delivery ([dim_product_master](/dimension/dim_product_master.md)); NULL when no invoice line matched. |
| `mix_date` | DATE | Invoice business date from fact_transaction_delivery. |
| `company_id` | STRING | MAC5 company code from fact_transaction_delivery. |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milMonth` | INT64 | Month part of the document date. |
| `milDay` | INT64 | Day part of the document date. |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milvnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milQuan` | FLOAT64 | SUM of `curated_mil.milQuan` over the grain. |
| `milAdisc` | FLOAT64 | SUM of `curated_mil.milAdisc`: the document-level discount allocated to the lines. |
| `milCog` | FLOAT64 | SUM of `curated_mil.milCog`: gross line amount excluding VAT, with salesperson shares already applied to split-sale lines. |
| `milDisca` | FLOAT64 | SUM of `curated_mil.milDisca`: line discount amount excluding VAT. |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, line net amount in THB. |
| `asatdate` | DATE | Build date of fact_transaction_delivery (CURRENT_DATE('Asia/Bangkok')). |

# How it is built

- Definition: `definitions/fact/fact_delivery.sqlx` (`type: "operations"`, tags `fact_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [validated_mac5.ttrip_document](/validated/validated_mac5/ttrip_document.md), [validated_mac5.ttrip](/validated/validated_mac5/ttrip.md), [validated_mac5.tdelivery](/validated/validated_mac5/tdelivery.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), [fact_table.fact_transaction_delivery](/fact/fact_transaction_delivery.md), [dimension_table.dim_delivery](/dimension/dim_delivery.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: full refresh each run (`type: "operations"`: `CREATE OR REPLACE TABLE ... CLUSTER BY FactDeliverySK`, no partition), tag `fact_daily`, after `dim_delivery`, `fact_transaction_delivery`, `dim_company`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,998,858 rows, 1.0 GB.

# Examples

Delivery outcome per day, selecting the original status groups before summing enrichment copies.
```sql
WITH delivery_status AS (
  SELECT DISTINCT companyID, documentID, item, Vehicle, DeliveryDate,
         Lattitude, Longtitude, Zone, Point,
         shipmentStatus_1, shipmentStatus_2, shipmentStatus_3
  FROM `databuffet-nonprd.fact_table.fact_delivery`
  WHERE companyID = 'ag01' AND DeliveryDate >= DATE '2026-10-01'
)
SELECT DeliveryDate, SUM(shipmentStatus_2) AS received, SUM(shipmentStatus_3) AS refused,
       SUM(shipmentStatus_1) AS not_delivered
FROM delivery_status
GROUP BY DeliveryDate ORDER BY DeliveryDate;
```
Original delivery-status groups of one document by vehicle, excluding invoice/product enrichment copies.
```sql
SELECT DISTINCT companyID, documentID, Vehicle, item, DeliveryDate,
       Lattitude, Longtitude, Zone, Point, totalItems, deliveryStatus_1, shipmentStatus_2
FROM `databuffet-nonprd.fact_table.fact_delivery`
WHERE documentID = '<invoice no>' AND companyID = 'ag01';
```

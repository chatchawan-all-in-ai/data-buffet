---
type: BigQuery Table
title: "dim_delivery"
description: "One row = one delivered invoice document (MAC5 IS document) per company with trip, vehicle, item quantity and preparation/release/receipt status counts."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_delivery
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_delivery.sqlx"
    title: "Dataform definition (dimension/dim_delivery.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Delivery-tracking dimension built from the MAC5 trip tables (`ttrip`, `ttrip_document`, `tdelivery`) joined to invoice lines in `curated_mil`. For each invoice document that appears on a delivery trip it counts how many vehicles and delivery dates were involved, how many distinct stock codes and how many item units, and splits those units by status: loaded on a truck or not, vehicle released or not, delivered/accepted, not yet delivered or refused by the customer. It is the source of `DeliverySK` for [fact_delivery](/fact/fact_delivery.md).

Used by: [fact_table.fact_delivery](/fact/fact_delivery.md).

# Grain and key

One row per (`companyID`, `documentID`) where `documentID` is the invoice/document number (`ttrip_document.fdocument`, which matches `milVnos` of IS lines linked to another document). `DeliverySK` is a stable surrogate key (existing documents keep it; new ones get `max_sk + ROW_NUMBER()` ordered by `companyID`, `documentID`). Trip items whose stock code starts with '8' are excluded.

# Schema

| Column | Type | Description |
|---|---|---|
| `DeliverySK` | INT64 | Stable surrogate key of the delivered document; never regenerated. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), joined on company id. |
| `companyID` | STRING | MAC5 company code. |
| `documentID` | STRING | Invoice/document number (`ttrip_document.fdocument`), the key together with company; matches `milVnos` / `mihVnos` of the invoice. |
| `totalVehicle` | INT64 | Count of distinct vehicles (`ttrip.fvehicle`) used to deliver the document. |
| `totalDeliveryDate` | INT64 | Count of distinct delivery dates (from `ttrip_document.fdatetime`, first 8 digits as yyyymmdd). |
| `totalStkcode` | INT64 | Count of distinct item codes (`fitem`, or `fitem2` when `fitem` does not match an invoice line) on the document. |
| `totalQty` | INT64 | Total item units: count of `ttrip_document` item rows for the document (each row counted once), after matching items to invoice lines. |
| `documentStatus_1` | INT64 | Units whose document is loaded on a truck ('จัดของขึ้นรถ': `fdocument` present). |
| `documentStatus_2` | INT64 | Units whose document is not yet loaded ('ยังไม่จัดของ'). |
| `deliveryStatus_1` | INT64 | Units on trips where the vehicle was released ('ปล่อยรถแล้ว': `ttrip.fpass_Date` present). |
| `deliveryStatus_2` | INT64 | Units on trips where the vehicle was not released ('ไม่ปล่อยรถ'). |
| `shipmentStatus_1` | INT64 | Units not yet delivered ('ยังไม่ส่งของ': no `tdelivery` serial number). |
| `shipmentStatus_2` | INT64 | Units delivered and accepted by the customer ('รับสินค้าแล้ว': `tdelivery` row present and `fcancel = '0'`). |
| `shipmentStatus_3` | INT64 | Units delivered but refused by the customer ('ลูกค้าไม่รับ': `tdelivery` row present and `fcancel` not '0'). |

# How it is built

- Definition: `definitions/dimension/dim_delivery.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [validated_mac5.ttrip_document](/validated/validated_mac5/ttrip_document.md), [validated_mac5.ttrip](/validated/validated_mac5/ttrip.md), [validated_mac5.tdelivery](/validated/validated_mac5/tdelivery.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `companyID` + `documentID`; updates all measures, inserts new documents, no delete. Reads the full trip tables each run (no date window). Runs after `dim_company`; the target table pre-exists in BigQuery.

# Examples

Documents still not delivered (any units pending) per company.

```sql
SELECT companyID, COUNT(*) AS documents, SUM(shipmentStatus_1) AS units_pending
FROM `databuffet-nonprd.dimension_table.dim_delivery`
WHERE shipmentStatus_1 > 0
GROUP BY companyID
ORDER BY documents DESC;
```

Documents refused by customers, largest first.

```sql
SELECT companyID, documentID, totalQty, shipmentStatus_3
FROM `databuffet-nonprd.dimension_table.dim_delivery`
WHERE shipmentStatus_3 > 0
ORDER BY shipmentStatus_3 DESC
LIMIT 50;
```

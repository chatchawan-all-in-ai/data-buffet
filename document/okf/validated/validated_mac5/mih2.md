---
type: BigQuery Table
title: "mih2"
description: "One row = one revision of a sales order extension record (per company), unique on (company_id, MIH2day, MIH2month, MIH2year, MIH2type, MIH2vnos, MIH2cus, MIH2rev)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mih2&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mih2
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mih2.sqlx"
    title: "Dataform definition (validated/mac5/mih2.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `mih2`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Extra sales order (`PS`) data for ag01: salesperson split shares, ship-to and contact details, project, installation and status fields, one row per order revision.

Read by: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_view.view_dim_order](/view/dimension_view/view_dim_order.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md).

# Grain and key

One row per `company_id`, `MIH2day`, `MIH2month`, `MIH2year`, `MIH2type`, `MIH2vnos`, `MIH2cus`, `MIH2rev`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `mih2day` | INT64 | Day part of the sales order date. |
| `mih2month` | INT64 | Month part of the sales order date. |
| `mih2year` | INT64 | Year part of the sales order date (Gregorian). |
| `mih2type` | STRING | Document type code (PS = sales order). |
| `mih2vnos` | STRING | Sales order number, matching `mihvnos` of the `PS` header. |
| `mih2cus` | STRING | Customer code of the sales order, matching `deb.debcode`. |
| `mih2rev` | INT64 | Revision number of the sales order (highest = latest). |
| `mih2shpid` | INT64 | Ship-to address ID. |
| `mih2ponum` | STRING | Customer purchase-order number. |
| `mih2postat` | INT64 | Purchase-order status flag (-1 = set). |
| `mih2perpc` | STRING | Sales share of the main salesperson, as percent text (e.g. `70%`). |
| `mih2per2` | STRING | Employee code of the second salesperson sharing the sale. |
| `mih2per2pc` | STRING | Sales share of the second salesperson, as percent text (e.g. `30%`). |
| `mih2poprice` | FLOAT64 | Purchase-order price amount. |
| `mih2discextrano` | STRING | Extra discount number applied to the order (`NONE` when none). |
| `mih2projectname` | STRING | Project or site name of the order. |
| `mih2shipto_addr_no` | STRING | Ship-to address: house number. |
| `mih2shipto_addr_soi` | STRING | Ship-to address: soi (lane). |
| `mih2shipto_addr_road` | STRING | Ship-to address: road. |
| `mih2shipto_addr_tambol` | STRING | Ship-to address: sub-district (tambon). |
| `mih2shipto_addr_amphur` | STRING | Ship-to address: district (amphoe). |
| `mih2shipto_addr_province` | STRING | Ship-to address: province. |
| `mih2shipto_receiver1_name` | STRING | Name of the first goods receiver at the ship-to address. |
| `mih2shipto_receiver1_tel` | STRING | Phone number of the first goods receiver. |
| `mih2shipto_receiver2_name` | STRING | Name of the second goods receiver at the ship-to address. |
| `mih2shipto_receiver2_tel` | STRING | Phone number of the second goods receiver. |
| `mih2pos` | STRING | Ship-to location of the order (customer branch, plot or house). |
| `mih2co_name` | STRING | Coordinator (contact person) name. |
| `mih2co_tel` | STRING | Coordinator phone number. |
| `mih2co_fax` | STRING | Coordinator fax number. |
| `mih2goods_receiver` | STRING | Name of the person receiving the goods. |
| `mih2goods_receiver_pos` | STRING | Position of the person receiving the goods. |
| `mih2goods_to` | STRING | Delivery destination text (place name and address). |
| `mih2goods_to_tel` | STRING | Phone number at the delivery destination. |
| `mih2goods_to_fax` | STRING | Fax number at the delivery destination. |
| `mih2cus_type` | STRING | Customer type code. |
| `mih2cus_tel` | STRING | Customer phone number. |
| `mih2cus_fax` | STRING | Customer fax number. |
| `mih2cus_addr` | STRING | Customer address text. |
| `mih2cus_com` | STRING | Customer company name. |
| `mih2cus_name` | STRING | Customer name as printed on the order. |
| `mih2cushp_name` | STRING | Customer name for HomePro orders. |
| `mih2cus_code` | STRING | Alternative customer code. |
| `mih2cus_com_stat` | STRING | Customer company status. |
| `mih2cus_b` | STRING | Customer branch. |
| `mih2cusgrp` | STRING | Customer group or campaign reference of the order (e.g. a marketing or quotation number). |
| `mih2gp` | FLOAT64 | Gross profit amount of the order. |
| `mih2gppercen` | STRING | Gross profit percentage of the order. |
| `mih2install` | FLOAT64 | Installation charge amount. |
| `mih2trans` | FLOAT64 | Transport charge amount. |
| `mih2sumarea` | STRING | Total area of the order. |
| `mih2sumquan` | STRING | Total quantity of the order. |
| `mih2notes` | STRING | Free-text notes of the order. |
| `mih2hpstat` | STRING | HomePro order status code. |
| `mih2comval` | FLOAT64 | Commission amount. |
| `mih2comper` | FLOAT64 | Commission rate in percent. |
| `mih2cost` | STRING | Cost markup text of the order (e.g. `+ 25.4`). |
| `mih2projtype` | STRING | Project type code (e.g. `LYN`). |
| `mih2projtype2` | STRING | Secondary project type code. |
| `mih2mip` | STRING | Reference to the attachment set of the order, matching `mip.mipvnos`. |
| `mih2custype` | STRING | Customer type of the order. |
| `mih2spc1` | STRING | Specification field 1 of the order. |
| `mih2spc2` | STRING | Specification field 2 of the order. |
| `mih2spc3` | STRING | Specification field 3 of the order. |
| `mih2spc4` | STRING | Specification field 4 of the order. |
| `mih2spc5` | STRING | Specification field 5 of the order. |
| `mih2spc6` | STRING | Specification field 6 of the order. |
| `mih2spc7` | STRING | Specification field 7 of the order. |
| `mih2spc8` | STRING | Specification field 8 of the order. |
| `mih2spc9` | STRING | Specification field 9 of the order. |
| `mih2spc10` | STRING | Specification field 10 of the order. |
| `mih2spc11` | STRING | Specification field 11 of the order. |
| `mih2spc12` | STRING | Specification field 12 of the order. |
| `mih2wty` | STRING | Warranty information of the order. |
| `mih2tenwhe` | STRING | Flag: ten-wheel truck required for delivery. |
| `mih2sixwhe` | STRING | Flag: six-wheel truck required for delivery. |
| `mih2picup` | STRING | Flag: pickup truck required for delivery. |
| `mih2car` | STRING | Vehicle required for delivery. |
| `mih2mtc` | STRING | Maintenance contract information. |
| `mih2olddoor` | STRING | Existing (old) door details at the installation site. |
| `mih2oldwall` | STRING | Existing (old) wall details at the installation site. |
| `mih2oldrang` | STRING | Existing (old) rail details at the installation site. |
| `mih2oldmotor` | STRING | Existing (old) motor details at the installation site. |
| `mih2payment1` | STRING | Instalment payment 1 amount. |
| `mih2paydate1` | DATETIME | Instalment payment 1 date. |
| `mih2payment2` | STRING | Instalment payment 2 amount. |
| `mih2paydate2` | DATETIME | Instalment payment 2 date. |
| `mih2payment3` | STRING | Instalment payment 3 amount. |
| `mih2paydate3` | DATETIME | Instalment payment 3 date. |
| `mih2payinstall` | STRING | Installation payment amount. |
| `mih2billname` | STRING | Name to print on the bill. |
| `mih2accname` | STRING | Account name for payment. |
| `mih2foottel` | STRING | Phone number printed in the document footer. |
| `mih2footfax` | STRING | Fax number printed in the document footer. |
| `mih2billdate` | DATETIME | Billing date of the order. |
| `mih2chequedate` | DATETIME | Cheque collection date of the order. |
| `mih2employno` | STRING | Employee number of the installer or staff assigned. |
| `mih2foreman` | STRING | Foreman assigned to the order. |
| `mih2sendto` | DATETIME | Date the order was sent onward for processing. |
| `mih2complete` | DATETIME | Date the order was completed. |
| `mih2employee` | STRING | Staff member assigned to the order. |
| `mih2empaddr` | STRING | Address of the staff member assigned. |
| `mih2plnhouse` | STRING | House plan or model name of the project. |
| `mih2lbl1` | STRING | Label field 1 of the order form (lbl1 usually holds a salesperson code). |
| `mih2lbl2` | STRING | Label field 2 of the order form (lbl1 usually holds a salesperson code). |
| `mih2lbl3` | STRING | Label field 3 of the order form (lbl1 usually holds a salesperson code). |
| `mih2lbl4` | STRING | Label field 4 of the order form (lbl1 usually holds a salesperson code). |
| `mih2lbl5` | STRING | Label field 5 of the order form (lbl1 usually holds a salesperson code). |
| `mih2lbl6` | STRING | Label field 6 of the order form (lbl1 usually holds a salesperson code). |
| `mih2txt1` | FLOAT64 | Text field 1 of the order form (usually an amount figure). |
| `mih2txt2` | FLOAT64 | Text field 2 of the order form (usually an amount figure). |
| `mih2txt3` | FLOAT64 | Text field 3 of the order form (usually an amount figure). |
| `mih2txt4` | FLOAT64 | Text field 4 of the order form (usually an amount figure). |
| `mih2txt5` | FLOAT64 | Text field 5 of the order form (usually an amount figure). |
| `mih2txt6` | FLOAT64 | Text field 6 of the order form (usually an amount figure). |
| `mih2txt7` | FLOAT64 | Text field 7 of the order form (usually an amount figure). |
| `mih2txt8` | FLOAT64 | Text field 8 of the order form (usually an amount figure). |
| `mih2txt9` | FLOAT64 | Text field 9 of the order form (usually an amount figure). |
| `mih2txt10` | FLOAT64 | Text field 10 of the order form (usually an amount figure). |
| `mih2status` | INT64 | Sales order status code, as in `ar_s` (e.g. 25 = awaiting approval, 26 = approved). |
| `mih2hw1` | INT64 | Hardware item 1 selection of the order. |
| `mih2hw2` | INT64 | Hardware item 2 selection of the order. |
| `mih2hw3` | INT64 | Hardware item 3 selection of the order. |
| `mih2hw4` | INT64 | Hardware item 4 selection of the order. |
| `mih2hw5` | INT64 | Hardware item 5 selection of the order. |
| `mih2hw6` | INT64 | Hardware item 6 selection of the order. |
| `mih2hw7` | INT64 | Hardware item 7 selection of the order. |
| `mih2hw8` | INT64 | Hardware item 8 selection of the order. |
| `mih2hw9` | INT64 | Hardware item 9 selection of the order. |
| `mih2hw10` | INT64 | Hardware item 10 selection of the order. |
| `mih2hw11` | INT64 | Hardware item 11 selection of the order. |
| `mih2hw12` | INT64 | Hardware item 12 selection of the order. |
| `mih2hw13` | INT64 | Hardware item 13 selection of the order. |
| `mih2hw14` | INT64 | Hardware item 14 selection of the order. |
| `mih2hw15` | INT64 | Hardware item 15 selection of the order. |
| `mih2hwrem` | STRING | Remark for the hardware items of the order. |
| `mih2desc` | STRING | Free-text description of the order. |
| `mih2updateby` | STRING | User code of the person who last updated the record. |
| `mih2updatenamet` | STRING | Thai first name of the person who last updated the record. |
| `mih2crdate` | DATETIME | Date and time the record was created. |
| `mih2updatedate` | DATETIME | Date and time the record was last updated. |
| `paymentstatus` | INT64 | Payment status flag of the order (0 or 1). |
| `condpack` | INT64 | Packing condition of the order. |
| `installstatus` | STRING | Installation status text (e.g. installation handed over). |
| `inv_percen` | FLOAT64 | Invoiced percentage of the order. |
| `maxrev` | INT64 | Revision marker flag of the record (0 or 1). |
| `mih2vnos_core` | STRING | Original (core) order number the record derives from. |
| `projcode` | STRING | Project code of the order. |
| `transtatus` | STRING | Transport status of the order. |
| `packstatus` | STRING | Goods-issue status text (fully issued or partly issued). |
| `bominstallstatus` | STRING | Installation status of the bill of materials. |
| `mustinstall` | INT64 | Flag: installation required (1 = yes). |
| `direction` | INT64 | Direction code of the order (0, 1, 2). |
| `poexpiredate` | DATETIME | Expiry date of the customer purchase order. |
| `insfinishdate` | DATETIME | Date the installation was finished. |
| `sendcusthome` | INT64 | Flag: deliver to the customer's home (1 = yes). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mih2.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mih2](/initial/raw_mac5_ag01/mih2.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `mih2type`, `mih2vnos`, `mih2cus`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mih2`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MIH2day, MIH2month, MIH2year, MIH2type, MIH2vnos, MIH2cus, MIH2rev, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mih2`
GROUP BY company_id, MIH2day, MIH2month, MIH2year, MIH2type, MIH2vnos, MIH2cus, MIH2rev
HAVING n > 1
```

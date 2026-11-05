---
type: BigQuery Table
title: "deb"
description: "One row = one customer (debtor) (per company), unique on (company_id, debcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=deb&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: deb
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/deb.sqlx"
    title: "Dataform definition (validated/mac5/deb.sqlx)"
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

Validated copy of MAC5 `deb` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Customer master of the MAC5 ERP: names, addresses, tax ID, group, grade, salesperson, credit limit and terms.

Read by: [process_dataset.deb_address_data](/process/deb_address_data.md), [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), [cdc_dataset.cdc_change_log](/cdc/cdc_change_log.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md), [dimension_table.dim_delivery](/dimension/dim_delivery.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [fact_table.fact_delivery](/fact/fact_delivery.md), [fact_table.fact_transcation](/fact/fact_transcation.md), [pub_sub.export_company](/view/pub_sub/export_company.md).

# Grain and key

One row per `company_id`, `debcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `debcode` | STRING | Customer (debtor) code. |
| `debgroup` | STRING | Customer group code (e.g. HP, TW, BT, GB, MH, DOHOME); drives channel matching in the sale-rep rules. |
| `debnamet` | STRING | Customer name in Thai. |
| `debnamee` | STRING | Customer name in English. |
| `debcontactt` | STRING | Contact person name in Thai. |
| `debcontacte` | STRING | Contact person name in English. |
| `debadd1at` | STRING | Thai address line 1 of the customer. |
| `debadd2at` | STRING | Thai address line 2 of the customer. |
| `debadd3at` | STRING | Thai address line 3 of the customer. |
| `debadd1ae` | STRING | English address line 1 of the customer. |
| `debadd2ae` | STRING | English address line 2 of the customer. |
| `debadd3ae` | STRING | English address line 3 of the customer. |
| `debtel` | STRING | Phone number(s) of the customer. |
| `debtaxnos` | STRING | 13-digit tax ID of the customer. |
| `debzone` | STRING | Sales zone code of the customer (e.g. `001`, `D-001`). |
| `debgrade` | STRING | Customer grade code. |
| `deblimit` | FLOAT64 | Credit limit of the customer in baht. |
| `debtaxclass` | FLOAT64 | VAT rate applied to the customer in percent (7 or 0). |
| `debgoodsdef` | FLOAT64 | Default goods discount of the customer. |
| `debcreditterm` | INT64 | Credit term in days. |
| `debpaytype` | INT64 | Payment schedule type code (1, 2). |
| `debpayday` | INT64 | Payment day setting of the payment schedule. |
| `debpayon1` | INT64 | Payment day 1 of the payment schedule. |
| `debpayon2` | INT64 | Payment day 2 of the payment schedule. |
| `debpayon3` | INT64 | Payment day 3 of the payment schedule. |
| `debpayon4` | INT64 | Payment day 4 of the payment schedule. |
| `debpayon5` | INT64 | Payment day 5 of the payment schedule. |
| `debpayn1` | INT64 | Payment schedule parameter 1. |
| `debpayn2` | INT64 | Payment schedule parameter 2. |
| `debbgrtype` | INT64 | Billing schedule type code. |
| `debbgrday` | INT64 | Billing day setting of the billing schedule. |
| `debbgron1` | INT64 | Billing day 1 of the billing schedule. |
| `debbgron2` | INT64 | Billing day 2 of the billing schedule. |
| `debbgron3` | INT64 | Billing day 3 of the billing schedule. |
| `debbgron4` | INT64 | Billing day 4 of the billing schedule. |
| `debbgron5` | INT64 | Billing day 5 of the billing schedule. |
| `debdate` | DATETIME | Date the customer record was created. |
| `debhide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `debfax` | STRING | Fax number of the customer. |
| `debemail` | STRING | Email address of the customer. |
| `debtarget` | FLOAT64 | Sales target of the customer. |
| `debmemo` | STRING | Free-text memo on the customer. |
| `debac` | STRING | AR GL account code of the customer (e.g. `112200`). |
| `deblock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `deboname` | STRING | Other name of the customer (e.g. branch label). |
| `debcm1` | STRING | Comment field 1 of the customer. |
| `debcm2` | STRING | Comment field 2 of the customer. |
| `debcm3` | STRING | Comment field 3 of the customer. |
| `debcm4` | STRING | Comment field 4 of the customer. |
| `debcm5` | STRING | Comment field 5 of the customer. |
| `debcm6` | STRING | Comment field 6 of the customer. |
| `debcm7` | STRING | Comment field 7 of the customer. |
| `debcm8` | STRING | Comment field 8 of the customer. |
| `debcm9` | STRING | Comment field 9 of the customer. |
| `debcm10` | STRING | Comment field 10 of the customer. |
| `debprice` | STRING | Default price level code of the customer. |
| `debeditlk` | DATETIME | Date and time the record was locked for editing. |
| `debrefwe` | STRING | External reference code of the record. |
| `debbillad` | INT64 | Billing-address flag of the customer. |
| `debsortnt` | STRING | Thai sort key of the customer (usually the Thai name). |
| `debsortne` | STRING | English sort key of the customer. |
| `debeditdt` | DATETIME | Date and time the record was last edited. |
| `debeditmf` | STRING | User code of the person who last edited the record. |
| `debinex` | INT64 | VAT include/exclude flag of the customer's prices (`1`, `0`). |
| `debsalesp` | STRING | Salesperson code assigned to the customer (joins `per.percode`). |
| `debbranch` | STRING | Tax branch number of the customer (`00000` = head office). |
| `debxxxx` | STRING | Secondary salesperson (employee) code of the customer. |
| `debbusinesstype` | STRING | Business type code of the customer. |
| `debbusinessdesc` | STRING | Business type description of the customer. |
| `debactive` | INT64 | Active flag of the customer. |
| `debstatus` | INT64 | Status code of the customer (0 = normal). |
| `debexpiredate` | DATETIME | Expiry date of the customer record. |

# How it is built

- Definition: `definitions/validated/mac5/deb.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.deb](/initial/raw_mac5_ag01/deb.md), [raw_mac5_aa05.deb](/initial/raw_mac5_aa05/deb.md), [raw_mac5_ab01.deb](/initial/raw_mac5_ab01/deb.md), [raw_mac5_ac02.deb](/initial/raw_mac5_ac02/deb.md), [raw_mac5_ak02.deb](/initial/raw_mac5_ak02/deb.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY debnamet desc, debnamee desc, debdate desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `debcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.deb`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, debcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.deb`
GROUP BY company_id, debcode
HAVING n > 1
```

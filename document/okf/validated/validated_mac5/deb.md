---
type: BigQuery Table
title: "deb"
description: "One row = one debtor / customer master, unique on (company_id, debcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=deb&page=table"
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `deb` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: debtor / customer master. Table meaning is inferred from column prefixes.
Used by: [process_dataset.deb_address_data](/process/deb_address_data.md), [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), [cdc_dataset.cdc_change_log](/cdc/cdc_change_log.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md), [dimension_table.dim_delivery](/dimension/dim_delivery.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [fact_table.fact_delivery](/fact/fact_delivery.md), [fact_table.fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per `company_id`, `debcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `debcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `debgroup` | STRING | Meaning not documented in the repo. |
| `debnamet` | STRING | Meaning not documented in the repo. |
| `debnamee` | STRING | Meaning not documented in the repo. |
| `debcontactt` | STRING | Meaning not documented in the repo. |
| `debcontacte` | STRING | Meaning not documented in the repo. |
| `debadd1at` | STRING | Meaning not documented in the repo. |
| `debadd2at` | STRING | Meaning not documented in the repo. |
| `debadd3at` | STRING | Meaning not documented in the repo. |
| `debadd1ae` | STRING | Meaning not documented in the repo. |
| `debadd2ae` | STRING | Meaning not documented in the repo. |
| `debadd3ae` | STRING | Meaning not documented in the repo. |
| `debtel` | STRING | Meaning not documented in the repo. |
| `debtaxnos` | STRING | Meaning not documented in the repo. |
| `debzone` | STRING | Meaning not documented in the repo. |
| `debgrade` | STRING | Meaning not documented in the repo. |
| `deblimit` | FLOAT64 | Meaning not documented in the repo. |
| `debtaxclass` | FLOAT64 | Meaning not documented in the repo. |
| `debgoodsdef` | FLOAT64 | Meaning not documented in the repo. |
| `debcreditterm` | INT64 | Meaning not documented in the repo. |
| `debpaytype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `debpayday` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `debpayon1` | INT64 | Meaning not documented in the repo. |
| `debpayon2` | INT64 | Meaning not documented in the repo. |
| `debpayon3` | INT64 | Meaning not documented in the repo. |
| `debpayon4` | INT64 | Meaning not documented in the repo. |
| `debpayon5` | INT64 | Meaning not documented in the repo. |
| `debpayn1` | INT64 | Meaning not documented in the repo. |
| `debpayn2` | INT64 | Meaning not documented in the repo. |
| `debbgrtype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `debbgrday` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `debbgron1` | INT64 | Meaning not documented in the repo. |
| `debbgron2` | INT64 | Meaning not documented in the repo. |
| `debbgron3` | INT64 | Meaning not documented in the repo. |
| `debbgron4` | INT64 | Meaning not documented in the repo. |
| `debbgron5` | INT64 | Meaning not documented in the repo. |
| `debdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `debhide` | INT64 | Meaning not documented in the repo. |
| `debfax` | STRING | Meaning not documented in the repo. |
| `debemail` | STRING | Meaning not documented in the repo. |
| `debtarget` | FLOAT64 | Meaning not documented in the repo. |
| `debmemo` | STRING | Meaning not documented in the repo. |
| `debac` | STRING | Meaning not documented in the repo. |
| `deblock` | INT64 | Meaning not documented in the repo. |
| `deboname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `debcm1` | STRING | Meaning not documented in the repo. |
| `debcm2` | STRING | Meaning not documented in the repo. |
| `debcm3` | STRING | Meaning not documented in the repo. |
| `debcm4` | STRING | Meaning not documented in the repo. |
| `debcm5` | STRING | Meaning not documented in the repo. |
| `debcm6` | STRING | Meaning not documented in the repo. |
| `debcm7` | STRING | Meaning not documented in the repo. |
| `debcm8` | STRING | Meaning not documented in the repo. |
| `debcm9` | STRING | Meaning not documented in the repo. |
| `debcm10` | STRING | Meaning not documented in the repo. |
| `debprice` | STRING | Likely price (inferred from the column name only; not documented in the repo). |
| `debeditlk` | DATETIME | Meaning not documented in the repo. |
| `debrefwe` | STRING | Meaning not documented in the repo. |
| `debbillad` | INT64 | Meaning not documented in the repo. |
| `debsortnt` | STRING | Meaning not documented in the repo. |
| `debsortne` | STRING | Meaning not documented in the repo. |
| `debeditdt` | DATETIME | Meaning not documented in the repo. |
| `debeditmf` | STRING | Meaning not documented in the repo. |
| `debinex` | INT64 | Meaning not documented in the repo. |
| `debsalesp` | STRING | Meaning not documented in the repo. |
| `debbranch` | STRING | Meaning not documented in the repo. |
| `debxxxx` | STRING | Meaning not documented in the repo. |
| `debbusinesstype` | STRING | Meaning not documented in the repo. |
| `debbusinessdesc` | STRING | Meaning not documented in the repo. |
| `debactive` | INT64 | Meaning not documented in the repo. |
| `debstatus` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |
| `debexpiredate` | DATETIME | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/deb.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.deb](/initial/raw_mac5_ag01/deb.md), [raw_mac5_aa05.deb](/initial/raw_mac5_aa05/deb.md), [raw_mac5_ab01.deb](/initial/raw_mac5_ab01/deb.md), [raw_mac5_ac02.deb](/initial/raw_mac5_ac02/deb.md), [raw_mac5_ak02.deb](/initial/raw_mac5_ak02/deb.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY debnamet desc, debnamee desc, debdate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `debcode`.
- Approximate size (BigQuery metadata, 2026-10-31): 98,321 rows, 43.3 MB.

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

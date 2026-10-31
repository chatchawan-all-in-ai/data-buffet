---
type: BigQuery Table
title: "mih2"
description: "One row = one document header revision, unique on (company_id, MIH2day, MIH2month, MIH2year, MIH2type, MIH2vnos, MIH2cus, MIH2rev)."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `mih2`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: document header revision. Table meaning is inferred from column prefixes.
Used by: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_view.view_dim_order](/view/dimension_view/view_dim_order.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md).

# Grain and key

One row per `company_id`, `MIH2day`, `MIH2month`, `MIH2year`, `MIH2type`, `MIH2vnos`, `MIH2cus`, `MIH2rev`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `mih2day` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `mih2month` | INT64 | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `mih2year` | INT64 | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `mih2type` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `mih2vnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `mih2cus` | STRING | Likely customer code (inferred from the column name only; not documented in the repo). |
| `mih2rev` | INT64 | Meaning not documented in the repo. |
| `mih2shpid` | INT64 | Meaning not documented in the repo. |
| `mih2ponum` | STRING | Meaning not documented in the repo. |
| `mih2postat` | INT64 | Meaning not documented in the repo. |
| `mih2perpc` | STRING | Meaning not documented in the repo. |
| `mih2per2` | STRING | Meaning not documented in the repo. |
| `mih2per2pc` | STRING | Meaning not documented in the repo. |
| `mih2poprice` | FLOAT64 | Likely price (inferred from the column name only; not documented in the repo). |
| `mih2discextrano` | STRING | Meaning not documented in the repo. |
| `mih2projectname` | STRING | Meaning not documented in the repo. |
| `mih2shipto_addr_no` | STRING | Meaning not documented in the repo. |
| `mih2shipto_addr_soi` | STRING | Meaning not documented in the repo. |
| `mih2shipto_addr_road` | STRING | Meaning not documented in the repo. |
| `mih2shipto_addr_tambol` | STRING | Meaning not documented in the repo. |
| `mih2shipto_addr_amphur` | STRING | Meaning not documented in the repo. |
| `mih2shipto_addr_province` | STRING | Meaning not documented in the repo. |
| `mih2shipto_receiver1_name` | STRING | Meaning not documented in the repo. |
| `mih2shipto_receiver1_tel` | STRING | Meaning not documented in the repo. |
| `mih2shipto_receiver2_name` | STRING | Meaning not documented in the repo. |
| `mih2shipto_receiver2_tel` | STRING | Meaning not documented in the repo. |
| `mih2pos` | STRING | Meaning not documented in the repo. |
| `mih2co_name` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `mih2co_tel` | STRING | Meaning not documented in the repo. |
| `mih2co_fax` | STRING | Meaning not documented in the repo. |
| `mih2goods_receiver` | STRING | Meaning not documented in the repo. |
| `mih2goods_receiver_pos` | STRING | Meaning not documented in the repo. |
| `mih2goods_to` | STRING | Meaning not documented in the repo. |
| `mih2goods_to_tel` | STRING | Meaning not documented in the repo. |
| `mih2goods_to_fax` | STRING | Meaning not documented in the repo. |
| `mih2cus_type` | STRING | Meaning not documented in the repo. |
| `mih2cus_tel` | STRING | Meaning not documented in the repo. |
| `mih2cus_fax` | STRING | Meaning not documented in the repo. |
| `mih2cus_addr` | STRING | Meaning not documented in the repo. |
| `mih2cus_com` | STRING | Meaning not documented in the repo. |
| `mih2cus_name` | STRING | Meaning not documented in the repo. |
| `mih2cushp_name` | STRING | Meaning not documented in the repo. |
| `mih2cus_code` | STRING | Meaning not documented in the repo. |
| `mih2cus_com_stat` | STRING | Meaning not documented in the repo. |
| `mih2cus_b` | STRING | Meaning not documented in the repo. |
| `mih2cusgrp` | STRING | Meaning not documented in the repo. |
| `mih2gp` | FLOAT64 | Meaning not documented in the repo. |
| `mih2gppercen` | STRING | Meaning not documented in the repo. |
| `mih2install` | FLOAT64 | Meaning not documented in the repo. |
| `mih2trans` | FLOAT64 | Meaning not documented in the repo. |
| `mih2sumarea` | STRING | Meaning not documented in the repo. |
| `mih2sumquan` | STRING | Meaning not documented in the repo. |
| `mih2notes` | STRING | Meaning not documented in the repo. |
| `mih2hpstat` | STRING | Meaning not documented in the repo. |
| `mih2comval` | FLOAT64 | Meaning not documented in the repo. |
| `mih2comper` | FLOAT64 | Meaning not documented in the repo. |
| `mih2cost` | STRING | Meaning not documented in the repo. |
| `mih2projtype` | STRING | Meaning not documented in the repo. |
| `mih2projtype2` | STRING | Meaning not documented in the repo. |
| `mih2mip` | STRING | Meaning not documented in the repo. |
| `mih2custype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `mih2spc1` | STRING | Meaning not documented in the repo. |
| `mih2spc2` | STRING | Meaning not documented in the repo. |
| `mih2spc3` | STRING | Meaning not documented in the repo. |
| `mih2spc4` | STRING | Meaning not documented in the repo. |
| `mih2spc5` | STRING | Meaning not documented in the repo. |
| `mih2spc6` | STRING | Meaning not documented in the repo. |
| `mih2spc7` | STRING | Meaning not documented in the repo. |
| `mih2spc8` | STRING | Meaning not documented in the repo. |
| `mih2spc9` | STRING | Meaning not documented in the repo. |
| `mih2spc10` | STRING | Meaning not documented in the repo. |
| `mih2spc11` | STRING | Meaning not documented in the repo. |
| `mih2spc12` | STRING | Meaning not documented in the repo. |
| `mih2wty` | STRING | Meaning not documented in the repo. |
| `mih2tenwhe` | STRING | Meaning not documented in the repo. |
| `mih2sixwhe` | STRING | Meaning not documented in the repo. |
| `mih2picup` | STRING | Meaning not documented in the repo. |
| `mih2car` | STRING | Meaning not documented in the repo. |
| `mih2mtc` | STRING | Meaning not documented in the repo. |
| `mih2olddoor` | STRING | Meaning not documented in the repo. |
| `mih2oldwall` | STRING | Meaning not documented in the repo. |
| `mih2oldrang` | STRING | Meaning not documented in the repo. |
| `mih2oldmotor` | STRING | Meaning not documented in the repo. |
| `mih2payment1` | STRING | Meaning not documented in the repo. |
| `mih2paydate1` | DATETIME | Meaning not documented in the repo. |
| `mih2payment2` | STRING | Meaning not documented in the repo. |
| `mih2paydate2` | DATETIME | Meaning not documented in the repo. |
| `mih2payment3` | STRING | Meaning not documented in the repo. |
| `mih2paydate3` | DATETIME | Meaning not documented in the repo. |
| `mih2payinstall` | STRING | Meaning not documented in the repo. |
| `mih2billname` | STRING | Meaning not documented in the repo. |
| `mih2accname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `mih2foottel` | STRING | Meaning not documented in the repo. |
| `mih2footfax` | STRING | Meaning not documented in the repo. |
| `mih2billdate` | DATETIME | Meaning not documented in the repo. |
| `mih2chequedate` | DATETIME | Meaning not documented in the repo. |
| `mih2employno` | STRING | Meaning not documented in the repo. |
| `mih2foreman` | STRING | Meaning not documented in the repo. |
| `mih2sendto` | DATETIME | Meaning not documented in the repo. |
| `mih2complete` | DATETIME | Meaning not documented in the repo. |
| `mih2employee` | STRING | Meaning not documented in the repo. |
| `mih2empaddr` | STRING | Meaning not documented in the repo. |
| `mih2plnhouse` | STRING | Meaning not documented in the repo. |
| `mih2lbl1` | STRING | Meaning not documented in the repo. |
| `mih2lbl2` | STRING | Meaning not documented in the repo. |
| `mih2lbl3` | STRING | Meaning not documented in the repo. |
| `mih2lbl4` | STRING | Meaning not documented in the repo. |
| `mih2lbl5` | STRING | Meaning not documented in the repo. |
| `mih2lbl6` | STRING | Meaning not documented in the repo. |
| `mih2txt1` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt2` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt3` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt4` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt5` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt6` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt7` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt8` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt9` | FLOAT64 | Meaning not documented in the repo. |
| `mih2txt10` | FLOAT64 | Meaning not documented in the repo. |
| `mih2status` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |
| `mih2hw1` | INT64 | Meaning not documented in the repo. |
| `mih2hw2` | INT64 | Meaning not documented in the repo. |
| `mih2hw3` | INT64 | Meaning not documented in the repo. |
| `mih2hw4` | INT64 | Meaning not documented in the repo. |
| `mih2hw5` | INT64 | Meaning not documented in the repo. |
| `mih2hw6` | INT64 | Meaning not documented in the repo. |
| `mih2hw7` | INT64 | Meaning not documented in the repo. |
| `mih2hw8` | INT64 | Meaning not documented in the repo. |
| `mih2hw9` | INT64 | Meaning not documented in the repo. |
| `mih2hw10` | INT64 | Meaning not documented in the repo. |
| `mih2hw11` | INT64 | Meaning not documented in the repo. |
| `mih2hw12` | INT64 | Meaning not documented in the repo. |
| `mih2hw13` | INT64 | Meaning not documented in the repo. |
| `mih2hw14` | INT64 | Meaning not documented in the repo. |
| `mih2hw15` | INT64 | Meaning not documented in the repo. |
| `mih2hwrem` | STRING | Meaning not documented in the repo. |
| `mih2desc` | STRING | Meaning not documented in the repo. |
| `mih2updateby` | STRING | Meaning not documented in the repo. |
| `mih2updatenamet` | STRING | Meaning not documented in the repo. |
| `mih2crdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `mih2updatedate` | DATETIME | Meaning not documented in the repo. |
| `paymentstatus` | INT64 | Meaning not documented in the repo. |
| `condpack` | INT64 | Meaning not documented in the repo. |
| `installstatus` | STRING | Meaning not documented in the repo. |
| `inv_percen` | FLOAT64 | Meaning not documented in the repo. |
| `maxrev` | INT64 | Meaning not documented in the repo. |
| `mih2vnos_core` | STRING | Meaning not documented in the repo. |
| `projcode` | STRING | Meaning not documented in the repo. |
| `transtatus` | STRING | Meaning not documented in the repo. |
| `packstatus` | STRING | Meaning not documented in the repo. |
| `bominstallstatus` | STRING | Meaning not documented in the repo. |
| `mustinstall` | INT64 | Meaning not documented in the repo. |
| `direction` | INT64 | Meaning not documented in the repo. |
| `poexpiredate` | DATETIME | Meaning not documented in the repo. |
| `insfinishdate` | DATETIME | Meaning not documented in the repo. |
| `sendcusthome` | INT64 | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mih2.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mih2](/initial/raw_mac5_ag01/mih2.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `mih2type`, `mih2vnos`, `mih2cus`.
- Approximate size (BigQuery metadata, 2026-10-31): 794,499 rows, 170.5 MB.

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

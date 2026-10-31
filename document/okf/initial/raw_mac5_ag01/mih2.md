---
type: BigQuery Table
title: "mih2"
description: "One row = one record of source table `mih2` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mih2&page=table"
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mih2/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mih2` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Used by: [validated_mac5.mih2](/validated/validated_mac5/mih2.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `mih2day` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2month` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2year` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2vnos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2rev` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shpid` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2ponum` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2postat` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2perpc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2per2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2per2pc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2poprice` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2discextrano` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2projectname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_addr_no` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_addr_soi` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_addr_road` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_addr_tambol` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_addr_amphur` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_addr_province` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_receiver1_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_receiver1_tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_receiver2_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2shipto_receiver2_tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2pos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2co_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2co_tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2co_fax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2goods_receiver` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2goods_receiver_pos` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2goods_to` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2goods_to_tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2goods_to_fax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_type` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_tel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_fax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_addr` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_com` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cushp_name` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_code` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_com_stat` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cus_b` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cusgrp` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2gp` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2gppercen` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2install` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2trans` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2sumarea` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2sumquan` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2notes` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hpstat` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2comval` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2comper` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2cost` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2projtype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2projtype2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2mip` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2custype` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc7` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc8` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc9` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc10` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc11` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2spc12` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2wty` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2tenwhe` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2sixwhe` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2picup` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2car` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2mtc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2olddoor` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2oldwall` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2oldrang` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2oldmotor` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2payment1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2paydate1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2payment2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2paydate2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2payment3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2paydate3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2payinstall` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2billname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2accname` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2foottel` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2footfax` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2billdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2chequedate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2employno` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2foreman` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2sendto` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2complete` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2employee` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2empaddr` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2plnhouse` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2lbl1` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2lbl2` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2lbl3` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2lbl4` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2lbl5` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2lbl6` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt1` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt2` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt3` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt4` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt5` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt6` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt7` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt8` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt9` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2txt10` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2status` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw1` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw2` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw3` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw4` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw5` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw6` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw7` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw8` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw9` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw10` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw11` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw12` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw13` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw14` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hw15` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2hwrem` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2desc` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2updateby` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2updatenamet` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2crdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2updatedate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `rowguid` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `paymentstatus` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `condpack` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `installstatus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `inv_percen` | FLOAT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `maxrev` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mih2vnos_core` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `projcode` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `transtatus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `packstatus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `bominstallstatus` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `mustinstall` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `direction` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `poexpiredate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `insfinishdate` | STRING | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `sendcusthome` | INT64 | Source column as delivered in the file, uncleaned (meaning not documented in the repo). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mih2/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mih2`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.mih2`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

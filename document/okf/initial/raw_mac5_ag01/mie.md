---
type: BigQuery Table
title: "mie"
description: "One row = one document's payment and withholding details, a record of source table `mie` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mie&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: mie
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mie/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mie` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Per-document payment details: instalment payment terms, cash and cheque amounts received or paid, and withholding tax entries (PND3 / PND53).

Read by: [validated_mac5.mie](/validated/validated_mac5/mie.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `mieday` | INT64 | Day part of the document date. |
| `miemonth` | INT64 | Month part of the document date. |
| `mieyear` | INT64 | Year part of the document date (Gregorian). |
| `mietype` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP). |
| `mievnos` | STRING | Document number, matching `mihvnos` of the same document type. |
| `miecus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `mierecdt3` | FLOAT64 | Withholding tax amount, first PND3 (individual) entry. |
| `mierecdt53` | FLOAT64 | Withholding tax amount, first PND53 (juristic person) entry. |
| `mierecdrnd` | FLOAT64 | Rounding difference on the receipt or payment. |
| `mierecdexg` | FLOAT64 | Exchange-rate difference on the receipt or payment. |
| `mierecdcsh` | FLOAT64 | Cash discount deducted on the receipt or payment. |
| `mierecdoth` | FLOAT64 | Other deductions on the receipt or payment, such as bank fees. |
| `mierecplus` | FLOAT64 | Additional amount added on the receipt or payment. |
| `miereccash` | FLOAT64 | Amount received or paid in cash or transfer. |
| `miereccqrd` | FLOAT64 | Amount received or paid by cheque. |
| `miectermcx` | STRING | Payment-term days per instalment, as a delimited text list (e.g. `60`). |
| `miectermpx` | STRING | Payment-term percentage per instalment, as a delimited text list (e.g. `100`). |
| `miectermax` | STRING | Payment-term amount per instalment, as a delimited text list. |
| `miectermdx` | STRING | Payment-term due date per instalment (`dd/mm/yyyy`), as a delimited text list. |
| `mietag` | INT64 | Tag marker of the record. |
| `miebasedt3` | FLOAT64 | Withholding tax base amount, first PND3 (individual) entry. |
| `miebasedt53` | FLOAT64 | Withholding tax base amount, first PND53 (juristic person) entry. |
| `miedescdt3` | STRING | Income type description of the first PND3 withholding entry (e.g. service fee, transport fee). |
| `miedescdt53` | STRING | Income type description of the first PND53 withholding entry (e.g. service fee, transport fee). |
| `miecondt3` | INT64 | Withholding condition code of the first PND3 entry (1 = withheld at source). |
| `miecondt53` | INT64 | Withholding condition code of the first PND53 entry (1 = withheld at source). |
| `mierecfc` | STRING | Amount in foreign currency on the receipt or payment. |
| `mierecdt32` | FLOAT64 | Withholding tax amount, second PND3 (individual) entry. |
| `mierecdt532` | FLOAT64 | Withholding tax amount, second PND53 (juristic person) entry. |
| `miebasedt32` | FLOAT64 | Withholding tax base amount, second PND3 (individual) entry. |
| `miebasedt532` | FLOAT64 | Withholding tax base amount, second PND53 (juristic person) entry. |
| `miedescdt32` | STRING | Income type description of the second PND3 withholding entry. |
| `miedescdt532` | STRING | Income type description of the second PND53 withholding entry. |
| `miecondt32` | INT64 | Withholding condition code of the second PND3 entry (1 = withheld at source). |
| `miecondt532` | INT64 | Withholding condition code of the second PND53 entry (1 = withheld at source). |
| `mieperdt3` | FLOAT64 | Withholding tax rate in percent, first PND3 entry. |
| `mieperdt32` | FLOAT64 | Withholding tax rate in percent, second PND3 entry. |
| `mieperdt53` | FLOAT64 | Withholding tax rate in percent, first PND53 entry. |
| `mieperdt532` | FLOAT64 | Withholding tax rate in percent, second PND53 entry. |
| `mietaxpayno` | STRING | Tax identification number of the withholding taxpayer. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mie/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mie`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.mie`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```

---
type: BigQuery Table
title: "mie_dummy"
description: "One row = one document's payment and withholding details (per company), unique on (company_id, MIEday, MIEmonth, MIEyear, MIEtype, MIEvnos, MIEcus)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mie_dummy&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mie_dummy
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mie_dummy.sqlx"
    title: "Dataform definition (validated/mac5/mie_dummy.sqlx)"
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

Validated copy of MAC5 `mie_dummy`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Per-document payment terms and withholding details from the ERP's dummy (staging) table, same layout as `mie`.
No other repo object reads it.

# Grain and key

One row per `company_id`, `MIEday`, `MIEmonth`, `MIEyear`, `MIEtype`, `MIEvnos`, `MIEcus`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
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
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mie_dummy.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mie_dummy](/initial/raw_mac5_ag01/mie_dummy.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `mietype`, `mievnos`, `miecus`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mie_dummy`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MIEday, MIEmonth, MIEyear, MIEtype, MIEvnos, MIEcus, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mie_dummy`
GROUP BY company_id, MIEday, MIEmonth, MIEyear, MIEtype, MIEvnos, MIEcus
HAVING n > 1
```

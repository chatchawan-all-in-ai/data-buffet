---
type: BigQuery Table
title: "deb_address_data"
description: "One row = the AI-parsed Thai address (sub-district, district, province in Thai and English) of one MAC5 customer (debtor) per company."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=deb_address_data&page=table"
tags: ["process", "mac5", "AI.GENERATE", "MAC5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/process/deb_address_data.sqlx"
    title: "Dataform definition (process/deb_address_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

AI address-parsing result for MAC5 customers (table `deb`): it concatenates the three address lines `debadd1at`, `debadd2at`, `debadd3at` into `raw_address` and asks BigQuery `AI.GENERATE` (endpoint gemini-3.5-flash-lite, temperature 0.1, an 'Expert Thai Geographic Data Extractor' prompt) to return sub-district, district and province names in Thai and English. The companion view [view_deb_address_data](/view/process_dataset/view_deb_address_data.md) joins the result to dim_sub_districts / dim_districts / dim_provinces; `fact_transcation` and `dim_customer` read that view for Province/District/SubDistrict keys.

# Grain and key

One row per `company_id` + `debcode` (the declared `uniqueKey`). Only customers whose address changed today (per CDC) are parsed and merged in a run; the others keep their earlier parsed row. Rows with a blank concatenated address are never parsed.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | MAC5 company code of the customer (validated_mac5.deb.company_id). |
| `debcode` | STRING | Customer (debtor) code (validated_mac5.deb.debcode). |
| `raw_address` | STRING | Trimmed concatenation of debadd1at, debadd2at and debadd3at separated by spaces: the exact text sent to the model. |
| `info` | STRUCT<DistrictEN STRING, DistrictTH STRING, ProvinceEN STRING, ProvinceTH STRING, SubDistrictEN STRING, SubDistrictTH STRING, full_response JSON, status STRING> | STRUCT returned by AI.GENERATE for the output schema: SubDistrictTH, SubDistrictEN, DistrictTH, DistrictEN, ProvinceTH, ProvinceEN (names without prefixes such as จ., อ., ต.; misspellings corrected; English is standard romanisation; postal code is validated against the province), plus the service fields full_response (JSON of the raw model response) and status (service status field, likely empty on success and an error text otherwise; not documented in the repo). AI output: validate before treating as master data. |

# How it is built

- Definition: `definitions/process/deb_address_data.sqlx` (`type: "incremental"`, tags `process`).
- `uniqueKey`: `company_id`, `debcode`.
- Storage options: `{"clusterBy": ["company_id", "debcode"]}`.
- Reads: [validated_mac5.deb](/validated/validated_mac5/deb.md), [cdc_dataset.cdc_change_log](/cdc/cdc_change_log.md).
- Incremental MERGE on `uniqueKey` (`type: "incremental"`, tag `process`; clustered by company_id, debcode; partition commented out). It declares no dependencies but is functionally gated on `cdc_dataset.cdc_change_log`: the SELECT keeps only `deb` rows whose key appears in cdc_change_log for source mac5 / validated_mac5 / deb with `asatdate = CURRENT_DATE('Asia/Bangkok')`, so `cdc` (cdc_change_log) runs first on the same day.
- Approximate size (BigQuery metadata, 2026-10-31): 7,188 rows, 6.9 MB.

# Examples

Parsed addresses that the model failed on or left empty (status check).

```sql
SELECT company_id, debcode, info.status
FROM `databuffet-nonprd.process_dataset.deb_address_data`
WHERE info.status IS NOT NULL AND info.status != ''
LIMIT 100
```

Customers per province (English) as parsed.

```sql
SELECT info.ProvinceEN AS province, COUNT(*) AS customers
FROM `databuffet-nonprd.process_dataset.deb_address_data`
GROUP BY province
ORDER BY customers DESC
```

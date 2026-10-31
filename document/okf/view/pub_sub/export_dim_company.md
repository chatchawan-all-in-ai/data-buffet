---
type: BigQuery View
title: "export_dim_company"
description: "One row = one company of dim_company exposed for the Pub/Sub export (data columns without SKs, plus row_key and row_hash)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_company&page=table"
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_company.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_company.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dim_company](/dimension/dim_company.md), part of the 'Data Mart to Pub/Sub' feed. It exposes the four business columns of the company dimension under their dim names (no surrogate key, no MdsId), plus `row_key` (the message `primary_key` as JSON) and `row_hash` (fingerprint of the message data). The Cloud Workflow `datamart-publish` (`document/how-to/setup-pubsub-export.md` in the repo) compares `row_hash` with the sent state in [mart_sent_state](/process/mart_sent_state.md) and publishes NEW/UPDATE/DELETE messages for changed rows. It is registered in [mart_export_config](/process/mart_export_config.md).

Used by [process_dataset.mart_export_config](/process/mart_export_config.md).

# Grain and key

One row per company: key `CompanyID` (unique and never NULL in `dim_company`); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanyID` | STRING | Company code (e.g. ag01) from `dim_company.CompanyID`; the natural key of the export and `primary_key` of the Pub/Sub message. |
| `CompanyCode` | STRING | Company code/short name from `dim_company.CompanyCode`. |
| `CompanyNameTH` | STRING | Company name in Thai from `dim_company.CompanyNameTH`. |
| `CompanyNameEN` | STRING | Company name in English from `dim_company.CompanyNameEN`. |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(CompanyID))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT(TO_JSON_STRING(c))` of the four data columns, i.e. of exactly the message `data`; changes only when a data column changes, so the publisher sends a row only when the hash differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_company.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_company](/dimension/dim_company.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; unlike other views it carries tags `view` and `pub_sub`; the `pub_sub` objects (dataset created by `pub_sub_schema`, this view, `mart_export_config`, `mart_sent_state`) are deployed by hand by running tag `pub_sub` and no scheduler runs it. It depends on `pub_sub_schema` (creates dataset `pub_sub`) and `dim_company`. The publisher also reads Dataform run status from the Dataform API to know when `dim_company` was refreshed.

# Examples

What would be published for all companies.

```sql
SELECT CompanyID, CompanyCode, CompanyNameTH, CompanyNameEN, row_key, row_hash
FROM `databuffet-nonprd.pub_sub.export_dim_company`
ORDER BY CompanyID
```

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_company`
GROUP BY row_key
HAVING n > 1
```

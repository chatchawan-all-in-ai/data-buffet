---
type: BigQuery Table
title: "business_unit_translations"
description: "One row per `business_unit_translations` from source table `business_unit_translations`, unique on (business_unit_id, language_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=business_unit_translations&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: business_unit_translations
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/business_unit_translations.sqlx"
    title: "Dataform definition (validated/master_sku/business_unit_translations.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki: validated layer"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T22:49:49+07:00" }
status: draft
---



# What it is

Validated copy of MASTER_SKU `business_unit_translations`: string values are cleaned, UTC datetimes are converted to Bangkok DATETIME values, the extract date is standardised to `asatdate`, and duplicate keys are collapsed. Table meaning: localized business unit names and descriptions.

# Grain and key

One row per (business_unit_id, language_id). The composite key is declared in `uniqueKey` and `pk_key`; the definition adds it as a `NOT ENFORCED` primary key after a full build.

# Schema

| Column | Type | Description |
|---|---|---|
| `business_unit_id` | STRING | Business unit identifier. |
| `language_id` | STRING | Language identifier. |
| `name` | STRING | Localized business unit name. |
| `description` | STRING | Localized business unit description. |
| `created_at` | DATETIME | Creation datetime converted from UTC to Asia/Bangkok. |
| `created_by` | STRING | Creator identifier. |
| `updated_at` | DATETIME | Update datetime converted from UTC to Asia/Bangkok. |
| `updated_by` | STRING | Updater identifier. |
| `asatdate` | DATE | Extract date parsed from the raw ASATDATE partition. |

# How it is built

- Definition: `definitions/validated/master_sku/business_unit_translations.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.business_unit_translations](../../initial/raw_master_sku/business_unit_translations.md).
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY business_unit_id, language_id ORDER BY asatdate DESC, updated_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by business_unit_id, language_id.

# Examples

Recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.business_unit_translations`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

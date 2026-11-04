---
type: BigQuery Table
title: "detail_sales_daily"
description: "One row = one article, branch and sales channel on one sale date from source table `detail_sales_daily`, unique on (sale_date, branch, article_id, distribution_channel)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=detail_sales_daily&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: detail_sales_daily
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_incremental", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/BT/detail_sales_daily.sqlx"
    title: "Dataform definition (validated/saleout_mdt/BT/detail_sales_daily.sqlx)"
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

Validated copy of SALEOUT_MDT `detail_sales_daily`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Boonthavorn (BT) daily sell-out of the company products per branch, article and channel (format used from 2026-10-08).
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `sale_date`, `branch`, `article_id`, `distribution_channel`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Sale date. |
| `branch` | STRING | Boonthavorn branch name in Thai, used as the branch code. |
| `article_id` | STRING | Boonthavorn article (product) code. |
| `distribution_channel` | STRING | Sales channel at Boonthavorn (`Showroom`, `Anyhome`, `Web`). |
| `net_inc_tax` | FLOAT64 | Net sales amount for the day including VAT (THB). |
| `sale_qty` | INT64 | Sales quantity for the day. |
| `sale_sqm` | FLOAT64 | Sales in square metres for the day. |
| `article_name_th` | STRING | Product name in Thai. |
| `brand` | STRING | Product brand. |
| `item_flag` | STRING | Item movement flag (`REGULAR`, `FAST`, `DISCON` = discontinued). |
| `flag_project` | STRING | Project-sale flag (`Project`/`Non-Project`). |
| `mch3` | STRING | Boonthavorn merchandise category, top level (department). |
| `mch2` | STRING | Boonthavorn merchandise category, second level. |
| `mch1` | STRING | Boonthavorn merchandise category, third level. |
| `mc` | STRING | Boonthavorn merchandise category, lowest level. |
| `vendor_id` | STRING | Boonthavorn vendor code of the supplier (the company), e.g. `10009`. |
| `vendor_name` | STRING | Supplier (vendor) name as registered at Boonthavorn. |
| `vendor_article` | STRING | Product code of the company (vendor) for the article; can be empty. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/BT/detail_sales_daily.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`, `saleout_daily`).
- Reads: [raw_saleout_mdt.detail_sales_daily](/initial/raw_saleout_mdt/detail_sales_daily.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `branch`, `article_id`, `sale_date`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.detail_sales_daily`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_date, branch, article_id, distribution_channel, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.detail_sales_daily`
GROUP BY sale_date, branch, article_id, distribution_channel
HAVING n > 1
```

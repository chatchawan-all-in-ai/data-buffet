---
type: BigQuery Table
title: "saleout_hp"
description: "One row = one article, branch and sale date from source table `saleout_hp`, unique on (siteno, artno, sale_date)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=saleout_hp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: saleout_hp
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_incremental", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/HP/saleout_hp.sqlx"
    title: "Dataform definition (validated/saleout_mdt/HP/saleout_hp.sqlx)"
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

Validated copy of SALEOUT_MDT `saleout_hp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Daily sell-out of the company products at HomePro and MegaHome branches (quantity and amount per article, branch and day).
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `siteno`, `artno`, `sale_date`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Sale date (= `perioddate`, one day before `crdate`). |
| `store_code` | STRING | Retail chain code derived from the branch: `HP` = HomePro, `MH` = MegaHome. |
| `siteno` | STRING | HomePro/MegaHome branch code (`S...` = HomePro, `M...` = MegaHome). |
| `sitename` | STRING | Branch name. |
| `artno` | STRING | HomePro article (product) number. |
| `artdesc` | STRING | HomePro article description (product name). |
| `vdartno` | STRING | Vendor article number: the GS1 barcode (starts with `885`) used to match `dim_product_master.Barcode`. |
| `vdartdesc` | STRING | Vendor article description as registered at HomePro. |
| `artean` | STRING | HomePro in-store EAN barcode (starts with `24`), not a product barcode. |
| `itemno` | STRING | Item sequence number of the article line in the report. |
| `mch3` | STRING | HomePro merchandise category code (e.g. `PB` = plumbing, `DW` = door and window). |
| `mch2desc` | STRING | HomePro merchandise category, second level, description. |
| `mch1desc` | STRING | HomePro merchandise category, lowest level, description. |
| `vendorno` | STRING | HomePro vendor number of the supplier (the company). |
| `vendorname` | STRING | Supplier (vendor) name as registered at HomePro. |
| `qty` | INT64 | Sales quantity (negative = return). |
| `value` | FLOAT64 | Sales amount (THB; negative = return). |
| `is_return` | BOOL | TRUE when the quantity is negative (a return). |
| `periodtype` | STRING | Report period type (`D` = daily, `M` = monthly). |
| `crdate` | DATETIME | Date-time HomePro created the report file (`DD/MM/YYYY HH:MM`). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/HP/saleout_hp.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`, `saleout_daily`).
- Reads: [raw_saleout_mdt.saleout_hp](/initial/raw_saleout_mdt/saleout_hp.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC, value DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `siteno`, `artno`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_hp`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT siteno, artno, sale_date, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_hp`
GROUP BY siteno, artno, sale_date
HAVING n > 1
```

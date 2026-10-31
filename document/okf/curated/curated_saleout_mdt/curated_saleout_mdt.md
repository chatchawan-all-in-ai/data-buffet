---
type: BigQuery Table
title: "curated_saleout_mdt"
description: "One row = the net sales (or returns) of one product at one modern-trade branch on one sale date and document type, merged from every chain feed."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_saleout_mdt&t=curated_saleout_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: curated_saleout_mdt
table_id: curated_saleout_mdt
tags: ["curated", "curated_saleout_mdt", "saleout", "curated_incremental", "saleout_daily", "SALEOUT_MDT"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/saleout_mdt/curated_saleout_mdt.sqlx"
    title: "Dataform definition (curated/saleout_mdt/curated_saleout_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Daily sell-out of the modern-trade (MDT) chains HomePro (HP), Mega Home (MH), Boonthavorn (BT), Global House (GB), Thai Watsadu (TW) and DoHome (DH), unified from the six different feed formats into one grain, plus a historical file (saleout_lastyear) for days before each chain's feed started. Feeds [curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md) (as DAILY_ROLLUP), fact_saleout_mdt and the dimensions dim_product_mdt and dim_sales_branch_mdt. Flag columns separate exact figures from derived or estimated ones.

# Grain and key

One row per `sale_date`, `store_code`, `branch_code`, `product_code`, `doc_type` (the declared `uniqueKey`). Sales channels are summed together; documents of type SALE and RETURN are separate rows. BT up to 2026-10-07 sends cumulative month-to-date figures that are differenced into daily amounts; rows covering several days carry `days_covered` > 1 and `date_is_estimated` = TRUE.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Day of the sale (business date). For BT feed rows covering several days it is the last day of the covered span. |
| `store_code` | STRING | Chain: HP, MH, BT, GB, TW or DH. For the HP file the value comes from validated saleout_hp (HP or MH); NULL marks sites that are not retail branches (CS01, EX99); NULL-store rows are ignored by the monthly rollup. |
| `branch_code` | STRING | Branch identifier in the convention of the chain: HP/MH SITENO, BT Thai branch name, GB branch code, TW full store string (e.g. '60001-CRC Thai Watsadu ...'), DH branch code (BI-history DH 'to go' codes get '_TG' appended). |
| `branch_name` | STRING | Branch name when the feed has one; BT and TW repeat the branch code; DH is NULL (real names come from the dimension). |
| `product_code` | STRING | Product key of the chain (HP ARTNO, BT article_id, GB 13-digit barcode, TW SKU without leading zeros, DH own code). |
| `product_name` | STRING | Product name from the feed. |
| `barcode_match` | STRING | Barcode used to match dim_product_master.Barcode: HP vdartno (GS1), GB the product code itself, TW the Barcode column; NULL for BT, DH and historical rows (they do not send barcodes). |
| `sale_qty` | INT64 | Quantity sold; negative for returns. For BT up to 2026-10-07 it is the difference of consecutive month-to-date quantities. |
| `sale_amount` | FLOAT64 | Sales amount in baht (for BT the NET_INC_TAX amount including VAT); negative for returns. |
| `doc_type` | STRING | SALE or RETURN. Sent by the chain for GB; derived by us for others (HP from the return flag, BT/TW/lastyear from the sign of the amount, DH from the return flag). |
| `doc_type_source` | STRING | SOURCE when the chain sent the document type (GB), DERIVED when we inferred it. |
| `days_covered` | INT64 | Number of days the row's figure covers: 1 for exact daily rows; for BT up to 2026-10-07 the gap in days since the previous snapshot of the file. |
| `date_is_estimated` | BOOL | TRUE when days_covered > 1 (BT multi-day span, actual sale day unknown); FALSE otherwise. |
| `asatdate` | DATE | Latest raw load date of the rows merged (for DH it is the last sale day in the file, not the DAG run date). |

# How it is built

- Definition: `definitions/curated/saleout_mdt/curated_saleout_mdt.sqlx` (`type: "incremental"`, tags `curated`, `curated_incremental`, `saleout_daily`).
- `uniqueKey`: `sale_date`, `store_code`, `branch_code`, `product_code`, `doc_type`.
- Storage options: `{"partitionBy": "sale_date", "clusterBy": ["store_code", "branch_code", "product_code"]}`.
- Reads: [validated_saleout_mdt.saleout_hp](/validated/validated_saleout_mdt/saleout_hp.md), [validated_saleout_mdt.sale_by_branch_detail](/validated/validated_saleout_mdt/sale_by_branch_detail.md), [validated_saleout_mdt.detail_sales_daily](/validated/validated_saleout_mdt/detail_sales_daily.md), [validated_saleout_mdt.saleout_gb](/validated/validated_saleout_mdt/saleout_gb.md), [validated_saleout_mdt.report_sale_subscription](/validated/validated_saleout_mdt/report_sale_subscription.md), [validated_saleout_mdt.saleout_dh](/validated/validated_saleout_mdt/saleout_dh.md), `validated_saleout_mdt.saleout_lastyear`.
- Incremental MERGE on `uniqueKey` (tags `curated`, `curated_incremental`, `saleout_daily`; depends on `curated_schema_saleout`). `pre_operations` builds a TEMP table from every chain CTE and, on incremental runs, DELETEs all existing rows of each (store_code, sale_date) present in it before the merge, so changed documents (e.g. SALE turned into RETURN) leave no stale rows. Only HP filters `asatdate` by `BACKFILL_DAYS`; the other chains read their validated tables in full every run. Partitioned by `sale_date`, clustered by store_code, branch_code, product_code.
- Approximate size (BigQuery metadata, 2026-10-31): 455,531 rows, 89.8 MB.

# Examples

Daily sales by chain for the last 30 days, excluding estimated-date rows.

```sql
SELECT sale_date, store_code, SUM(sale_amount) AS amount, SUM(sale_qty) AS qty
FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt`
WHERE sale_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 30 DAY)
  AND NOT date_is_estimated
GROUP BY sale_date, store_code
ORDER BY sale_date, store_code
```

Returns versus sales per chain for one month.

```sql
SELECT store_code, doc_type, SUM(sale_amount) AS amount
FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt`
WHERE sale_date BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'
GROUP BY store_code, doc_type
```

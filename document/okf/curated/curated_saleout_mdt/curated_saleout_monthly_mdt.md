---
type: BigQuery Table
title: "curated_saleout_monthly_mdt"
description: "One row = the monthly sell-out of one product at one branch of one modern-trade chain, taken from the single best source available for that chain and month."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_saleout_mdt&t=curated_saleout_monthly_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: curated_saleout_mdt
table_id: curated_saleout_monthly_mdt
tags: ["curated", "curated_saleout_mdt", "saleout", "curated_full", "saleout_daily", "SALEOUT_MDT"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/saleout_mdt/curated_saleout_monthly_mdt.sqlx"
    title: "Dataform definition (curated/saleout_mdt/curated_saleout_monthly_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Monthly sell-out table for modern-trade (MDT) chains; the source of fact_saleout_monthly_mdt (and referenced by the branch/product dimensions). It replaces the hand-built onetime.saleout_monthly_mdt. For each (month, chain) it picks ONE source by priority: 1 CHAIN_FILE (closing files the chain sends itself, curated_eom_gb/hp/tw/bt, from Aug 2026), 2 BI (history file from the BI team, 2022-01 to 2026-07, read from validated_saleout_mdt.saleout_lastyear_monthly), 3 DAILY_ROLLUP (rolled up from [curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md) for months/chains with neither). Related tables: [curated_eom_gb](/curated/curated_saleout_mdt/curated_eom_gb.md), [curated_eom_hp](/curated/curated_saleout_mdt/curated_eom_hp.md), [curated_eom_tw](/curated/curated_saleout_mdt/curated_eom_tw.md), [curated_eom_bt](/curated/curated_saleout_mdt/curated_eom_bt.md).

# Grain and key

Declared `uniqueKey`: `month_date`, `store_code`, `branch_code`, `product_code`. `month_date` has mixed grain: the LAST day of the month for closed months (all three sources), and the actual sale date (one value per day) for the current month, which comes from DAILY_ROLLUP. Exactly one source wins per (month, store_code) so the same month is never mixed across sources.

# Schema

| Column | Type | Description |
|---|---|---|
| `month_date` | DATE | Last day of the month for closed months; for the current month (DAILY_ROLLUP only) the individual sale date. |
| `store_code` | STRING | Chain code (HP, MH, GB, BT, TW, DH). |
| `branch_code` | STRING | Branch identifier in the convention of the chain (BT Thai branch name, TW full store string, DH branch codes with '_TG' appended for 'to go' branches from the BI file). |
| `branch_name` | STRING | Branch name when the source has one; NULL for TW and BT closing files and for DH. |
| `sales_channel` | STRING | Constant '-' (kept so the schema matches the old table; this grain has no channel). |
| `product_code` | STRING | Product code of the chain (HP ARTNO, BT article id, GB barcode, TW SKU without leading zeros, DH own code). |
| `product_name` | STRING | Product name from the source. |
| `sale_qty` | FLOAT64 | Quantity sold in the month (or day for the current month); negative for returns. |
| `sale_amount` | FLOAT64 | Sales amount in baht (BT/GB/TW closing files use the value including VAT, e.g. NET_INC_TAX for BT); negative for returns. |
| `source_type` | STRING | Which source won for this (month, chain): CHAIN_FILE, BI or DAILY_ROLLUP. |

# How it is built

- Definition: `definitions/curated/saleout_mdt/curated_saleout_monthly_mdt.sqlx` (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`).
- `uniqueKey`: `month_date`, `store_code`, `branch_code`, `product_code`.
- Storage options: `{"partitionBy": "month_date", "clusterBy": ["store_code", "branch_code", "product_code"]}`.
- Reads: [curated_saleout_mdt.curated_eom_gb](/curated/curated_saleout_mdt/curated_eom_gb.md), [curated_saleout_mdt.curated_eom_hp](/curated/curated_saleout_mdt/curated_eom_hp.md), [curated_saleout_mdt.curated_eom_tw](/curated/curated_saleout_mdt/curated_eom_tw.md), [curated_saleout_mdt.curated_eom_bt](/curated/curated_saleout_mdt/curated_eom_bt.md), `validated_saleout_mdt.saleout_lastyear_monthly`, [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).
- Full rebuild each run (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`; depends on `curated_schema_saleout`; reads the four curated_eom_* tables, curated_saleout_mdt and validated_saleout_mdt.saleout_lastyear_monthly, a table the repo does not create); partitioned by `month_date`, clustered by store_code, branch_code, product_code.
- Approximate size (BigQuery metadata, 2026-10-31): 373,203 rows, 63.0 MB.

# Examples

Monthly total per chain and source for one month.

```sql
SELECT store_code, source_type, SUM(sale_amount) AS amount, SUM(sale_qty) AS qty
FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_monthly_mdt`
WHERE DATE_TRUNC(month_date, MONTH) = DATE '2026-09-01'
GROUP BY store_code, source_type
```

Sell-out per month for one chain.

```sql
SELECT DATE_TRUNC(month_date, MONTH) AS month, SUM(sale_amount) AS amount
FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_monthly_mdt`
WHERE store_code = 'GB'
GROUP BY month
ORDER BY month
```

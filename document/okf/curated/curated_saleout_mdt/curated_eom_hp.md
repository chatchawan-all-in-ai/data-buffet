---
type: BigQuery Table
title: "curated_eom_hp"
description: "One row = the month-end sales total of one product at one HomePro (HP) or Mega Home (MH) site for one period, as reported by the chain."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_saleout_mdt&t=curated_eom_hp&page=table"
project_id: databuffet-nonprd
dataset_id: curated_saleout_mdt
table_id: curated_eom_hp
tags: ["curated", "curated_saleout_mdt", "saleout", "curated_full", "saleout_daily", "SALEOUT_MDT"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/saleout_mdt/curated_eom_hp.sqlx"
    title: "Dataform definition (curated/saleout_mdt/curated_eom_hp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Closing (EOM) sales file that HomePro and Mega Home send themselves (folder SO_MDT_EOM/HP); same layout as the daily saleout_hp feed except the period type is monthly. Kept as the figure 'as reported by the chain' and used as the CHAIN_FILE source of [curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md). One file holds both chains, split by site number.

# Grain and key

One row per `month_date` (first day of the period from PERIODDATE 'MM/YYYY'), `store_code` (HP or MH), `branch_code` (SITENO) and `product_code` (ARTNO). Declared `uniqueKey` is month_date, store_code, branch_code, product_code.

# Schema

| Column | Type | Description |
|---|---|---|
| `month_date` | DATE | First day of the period parsed from PERIODDATE (month/year, no day). |
| `store_code` | STRING | Chain: 'HP' for site numbers M888, CS01, EX99 or starting with 'S'; 'MH' for other sites starting with 'M'; NULL for any other prefix on purpose (to reveal a new chain). |
| `branch_code` | STRING | Site number (SITENO, cleaned). |
| `branch_name` | STRING | Site name (SITENAME); one value per key. |
| `product_code` | STRING | Article number (ARTNO), the product key also used by the daily feed. |
| `product_name` | STRING | Article description (ARTDESC). |
| `vdartno` | STRING | Vendor article number, a GS1 barcode (starts with 885) used to match dim_product_master.Barcode. The in-store barcode ARTEAN is not kept. |
| `sale_qty` | INT64 | Sum of QTY for the key. |
| `sale_amount` | FLOAT64 | Sum of VALUE for the key. |
| `crdate` | DATETIME | File creation timestamp stamped by the chain on each row (CRDATE, dd/mm/yyyy HH:MM); used to pick the newest version of a period; MAX over the key. |
| `asatdate` | DATE | Latest raw load date among the rows summed (the DAG run date, not the period). |

# How it is built

- Definition: `definitions/curated/saleout_mdt/curated_eom_hp.sqlx` (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`).
- `uniqueKey`: `month_date`, `store_code`, `branch_code`, `product_code`.
- Storage options: `{"partitionBy": "month_date", "clusterBy": ["store_code", "branch_code", "product_code"]}`.
- Reads: [raw_saleout_mdt.eom_hp](/initial/raw_saleout_mdt/eom_hp.md).
- Full rebuild each run (`type: "table"`, tags `curated`, `curated_full`, `saleout_daily`; depends on `curated_schema_saleout` and `create_all_table_raw_saleout_mdt`); partitioned by `month_date`, clustered by store_code, branch_code, product_code. Reads raw `eom_hp` directly.

# Examples

Month total per chain for one period.

```sql
SELECT month_date, store_code, SUM(sale_amount) AS amount, COUNT(*) AS n_rows
FROM `databuffet-nonprd.curated_saleout_mdt.curated_eom_hp`
WHERE month_date = DATE '2026-09-01'
GROUP BY month_date, store_code
```

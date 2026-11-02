---
okf_version: "0.2"
---
# Data Mart (data-buffet) knowledge bundle

One card per BigQuery table or view built by this repository's Dataform definitions in project `databuffet-nonprd`. [README](README.md) describes the bundle organisation and synchronization rule.

# Layers

* [Initial (raw)](initial/) - External tables over the AVRO/CSV files in `gs://file-raw-data`, one folder per raw dataset. (261 cards)
* [Validated](validated/) - Cleaned, typed and deduplicated copies of the raw tables, one folder per source system. (190 cards)
* [Curated](curated/) - Business logic over validated tables (MAC5, MASTERSKU, MASTER_SKU, SALEOUT_MDT). (14 cards)
* [Dimension](dimension/) - Star-schema dimensions in `dimension_table` (surrogate keys, mds and lake sourced). (71 cards)
* [Fact](fact/) - Star-schema facts in `fact_table` plus the AR chain. (18 cards)
* [View](view/) - BI/reporting views over dimensions, facts and curated tables. (41 cards)
* [Process](process/) - AI address parsing, RLS access map and the Pub/Sub export tables. (5 cards)
* [CDC](cdc/) - Change-data-capture log generated from `cdc-config.json`. (1 cards)
* [Org Center](org_center/) - Organisation structure (units, members, people, links, customer portfolios, exceptions, data-quality flags). (7 cards)

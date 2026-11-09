# Validated Layer — Source Inventory

> **LLM context**: Table-level inventory per source. Descriptions of MAC5 3-letter
> codes are inferred from column prefixes — verify in-file when it matters.
> Authoritative full-load list (all sources): `grep -rl 'TAG_VALIDATED_FULL' definitions/validated/`.
> Per-source file counts below are the point of this page; the layer total lives in the
> [generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview).

## MAC5 (87 files = 13 incremental + 73 full + 1 schema)

### Incremental (transactional)

| Table | Meaning (inferred) |
|---|---|
| `mih` / `mih2` / `mih_dummy` | invoice/document header (multi-company) / header revision / staging variant |
| `mil` / `mil_dummy` | invoice line items (multi-company) / variant |
| `mie` / `mie_dummy` | invoice extra/expense lines (multi-company) / variant |
| `mir` | invoice receipt/return lines (multi-company; tagged FULL) |
| `cps` / `cps_dummy` | cost-per-stock movement / variant |
| `cql` | quotation lines (multi-company) |
| `cst` | cost/stock transactions |
| `rcv` | receiving / goods receipt |

### Full-load families (73 tables, grouped)

- **Multi-company masters**: `ap_s, ar_s` (AP/AR status), `cfs` (cashflow), `chq`
  (cheques), `deb` (debtors/customers), `dep` (departments), `per` (personnel),
  `stg` (stock group), `stk` (stock master)
- **Billing**: `mih_billing, mil_billing, log_print_billing`
- **Docs/reference codes**: `doc, cpp, cpx, cre, rno, sbl, std, stf, sto, stgacc,
  stk_mkt, tab, vmp, mec, mip, check_po, grp`
- **Contract/quote-spread**: `maincontract, supcontract, main_qtspread,
  detail_qtspread, qt_spread_to_mih`
- **Booking (`tbook_*`)**: `tbook_apptype, tbook_givestk, tbook_payin,
  tbook_profilecomp, tbook_quodetail, tbook_quotation`; also `tbpjaddacc, tbcontact`
- **Distribution/approval (`tdis_*`) + logistics**: `tdis_approveorder, tdis_approveqt,
  tdis_mail, tdelivery, ttrip, ttrip_document`
- **Matching/BOT-RE**: `match_customer, match_product, match_deb_bot_re,
  product_bot_re, product_detail_bot_re`
- **Promotions/marketing**: `pro_ag, pro_crc, pro_re, product_promotion, mkt_per`
- **Combos**: `comboset, combostk`
- **PDF extracts per property developer**: `tmp_pdf_ap, tmp_pdf_frasers, tmp_pdf_pruksa,
  tmp_pdf_qh, tmp_pdf_sansiri, tmp_pdf_supalai`
- **Misc/ops**: `tmp_mihstatus, stg_report, pathfilestamper, tempgpsweb, apilog,
  userloginanyprogram, order_from_allkon_m`

## CIS360 (25 = 24 incremental + 1 schema) — PK `id`

- **Core**: `customer_profile`, `customer_address`, `juristic_profile`
- **Lookups**: `address_type, category, country, customer_status, customer_type,
  customer_profile_type, district, province, sub_district, zipcode, juristic_type,
  nature_business, organize_type, role_business, prefix`
- **Bridges**: `customer_profile_category, customer_profile_nature_business,
  customer_profile_role_business, customer_profile_tag, customer_to_customer,
  customer_to_platform, customer_to_transaction`

## MASTERSKU (12 = 11 incremental + 1 schema) — PK `prd_id` / `*_id`

`product` (SKU master), `product_detail` (JSON dims/specs), `product_category`,
`product_group`, `product_group_cost_group`, `product_status`, `product_admin_status`,
`brand`, `category`, `unit`, `vendor`

## SALEOUT_MDT (17 = 7 incremental + 9 full + 1 schema) — by retailer subfolder

| Folder | Table | Load | Tags |
|---|---|---|---|
| `BT/` | `sale_by_branch_detail` | incremental | `validated`, `validated_incremental` |
| `BT/` | `sales_by_branch`, `sale_by_branch_mch3`, `turnover`, `turnover_brand` | incremental | `validated` only |
| `BT/` | `stock_by_branch`, `stock_aging` | full (`type: "table"`) | `validated`, `validated_full` |
| `DH/` | `saleout_dh` | full, **latest file per period** (per source folder + month) | `validated`, `validated_full` |
| `EOM/` | `eom_bt`, `eom_gb`, `eom_hp`, `eom_tw` — month-end closing figures each retailer sends (raw folder `so_mdt_eom/`) | full, **latest delivery per month** | `validated`, `validated_full` |
| `GB/` | `saleout_gb` | incremental | `validated` only |
| `HP/` | `saleout_hp` | incremental | `validated`, `validated_incremental` |
| `TW/` | `report_sale_subscription` | full (no `uniqueKey`) | `validated`, `validated_full` |
| `LASTYEAR/` | `saleout_lastyear` — ไฟล์ Excel ย้อนหลังก่อนที่ TW จะส่ง feed (เพิ่ม 2026-09) · raw เป็น **CSV** | full (no `uniqueKey`) | `validated`, `validated_full` |

PKs are wide business composites (e.g. `["sale_no","sale_date","branch_code","product_code"]`).
"Latest per period" = a resent period keeps only its newest delivery
(`QUALIFY … = MAX(…) OVER (PARTITION BY <period>)`), see the
[full-load variants](validated-layer.md#full-load-pattern-tag_validated_full). End-to-end flow of this source (curated, dims,
facts, views, the 08:55 run): [source-systems § SALEOUT_MDT](../overview/source-systems.md#saleout_mdt--sell-out-modern-trade).

**2026-08-17** — all 10 incremental tables (ตอนนั้น) were brought onto the standard validated pattern: they gained
`partitionBy: "asatdate"` (they had `clusterBy` only, the single group in the whole
layer without a partition) and the incremental
`${when(incremental(), \`WHERE ASATDATE >= …BACKFILL_DAYS…\`)}` window, which they had
never had. Before that, every run rescanned the full raw history — ~1.2 GB/night to
produce ~80k rows, with `report_sale_subscription` alone at 721 MB.

The window is safe here: all 858 raw objects across the four retailer folders
(`hp` 84, `gb` 82, `tw` 84, `bt` 608) were uploaded on the same day as their own
`ASATDATE=` partition — **zero back-dated files** — so no vendor correction older
than `BACKFILL_DAYS` has ever arrived. If a retailer ever starts resending history,
raise `BACKFILL_DAYS` for that run instead of removing the window.

Downstream readers (since 2026-09/10): `curated_saleout_mdt` (sale feeds
`report_sale_subscription`, `sale_by_branch_detail`, `saleout_dh`, `saleout_gb`,
`saleout_hp`, `saleout_lastyear`), `curated_stock_mdt` (`stock_by_branch`,
`report_sale_subscription`) and `curated_saleout_monthly_mdt` (`eom_*` +
`curated_saleout_mdt`). The MDT facts read those curated tables, not validated.
`sales_by_branch`, `sale_by_branch_mch3`, `stock_aging`, `turnover` and `turnover_brand`
have no reader in the repo.

## MASTER_SKU — `master_sku` 3.0 (34 = 33 incremental + 1 schema)

Product master (`raw_master_sku` → `validated_master_sku` → `curated_master_sku`),
added 2026-10-12 and expanded 2026-11-08. All 33 table definitions use the standard
incremental pattern (tags `validated`, `validated_incremental`) and parse source UTC
datetimes with `parseFlexibleUtcDatetime`; `audit_logs` has no `updated_at`, so it
deduplicates by `created_at` after `asatdate`.

Raw source columns are retained. Tables partition by `asatdate` and cluster by their
keys; string key columns use `IFNULL(cleanString(...), '')` to avoid NULL MERGE keys.

| Group | Tables (PK) |
|---|---|
| Product | `products` (`id`), `product_translations` (`product_id`, `language_id`), `product_assets` (`id`), `product_channels` (`product_id`, `sales_channel_id`), `product_codes` (`id`), `product_groups` (`id`), `product_vendors` (`id`), `variant_definitions` (`id`) |
| Brand / vendor | `brands`, `vendors`, `brand_vendors` (`id`), `brand_translations` (`brand_id`, `language_id`) |
| Category | `categories` (`id`), `category_translations` (`category_id`, `language_id`) |
| Business / customer | `business_units` (`id`), `business_unit_translations` (`business_unit_id`, `language_id`), `channels` (`id`), `customers` (`id`), `product_channel_prices` (`product_id`, `sales_channel_id`, `business_unit_id`, `effective_date`), `product_customers` (`id`) |
| Functional groups | `functional_groups` (`id`), `functional_group_translations` (`functional_group_id`, `language_id`) |
| Codes | `common_codes` (`id`), `common_code_translations` (`common_code_id`, `language_id`) |
| Specs | `spec_groups`, `spec_attributes` (`id`), `spec_group_translations`, `spec_attribute_translations` (`*_id`, `language_id`), `specifications` (`group_id`, `attribute_id`) |
| Audit / access | `audit_logs` (`id`), `users` (`id`), `user_preferences` (`id`) |
| Search | `synonyms` (`id`) |

Direct readers are listed in each [validated MASTER_SKU card](../../okf/validated/validated_master_sku/index.md).
`products` carries the D365 cross-reference columns `d365_code`, `d365_size`,
`d365_style`, `d365_color`, `d365_configuration`, `d365_variant`
(`curated_products.prdD365Sku` = `d365_code`) — the likely join key to DERP
`item_number`.

## DERP (57 = 56 incremental + 1 schema)

DERP inventory, CRM and sales tables (`raw_derp` → `validated_derp`), GCS folder `derp_temp/`.
In the repo since `7819bef` (2026-10-17); the datasets were built by hand on 2026-10-16
as `raw_d365` / `validated_d365` (now `raw_derp` / `validated_derp`). The 23 `crm_*` and
5 `sales_*` tables were added 2026-10-28. Every table name equals its GCS folder name.

| Table | Load | PK | Notes |
|---|---|---|---|
| `inventory_movement_journal_headers` | incremental (`validated_incremental`) | `inventory_movement_journal_headers_id` | datetimes via `parseFlexibleUtcDatetime`; `is_active = 'Y'` |
| `inventory_movement_journal_entries` | incremental (`validated_incremental`) | `inventory_movement_journal_entries_id` | same as headers |
| `inventory_item_price` | incremental (`validated_incremental`) since 2026-10-28 (was full, latest partition only) | `inventory_item_price_id` | dedup `updated_datetime DESC, asatdate DESC`; rows deleted at source **stay** (no purge); datetimes via `parseFlexibleDatetime` because the source timezone is **unconfirmed**; `is_active = 'Yes'` |

**CRM / sales tables (28, all incremental, added 2026-10-28)** — one file per GCS folder,
columns taken from the real AVRO files (not the older schema workbook). PK = the first
column, the folder's `<name>_id` without the `crm_` / `sales_` prefix (e.g. `crm_quotation` →
`quotation_id`, `sales_employee` → `employee_id`); exceptions:
`sales_channel_master_sales_channel` → `master_sales_channel_id`, `sales_sales_territory` →
`sale_territory_id`. All keys were unique and non-null in the first files.

| Group | Tables |
|---|---|
| price | `crm_nd_sd_price`, `crm_nd_sd_price_territory_group`, `crm_nd_sd_price_zone` |
| quotation | `crm_quotation`, `crm_quotation_delivery`, `crm_quotation_delivery_detail`, `crm_quotation_detail`, `crm_quotation_history`, `crm_quotation_sale` |
| sale order | `crm_sale_order`, `crm_sale_order_approval_log`, `crm_sale_order_approver`, `crm_sale_order_attachment`, `crm_sale_order_delivery`, `crm_sale_order_delivery_line`, `crm_sale_order_deposit`, `crm_sale_order_line`, `crm_sale_order_payment`, `crm_sale_order_payment_allocation`, `crm_sale_order_payment_receipt`, `crm_sale_order_revision`, `crm_sale_order_sales_person`, `crm_sale_order_status_history` |
| sales master | `sales_channel_master_sales_channel`, `sales_customer_sales_territory`, `sales_employee`, `sales_employee_sale_territory`, `sales_sales_territory` |

Column rules shared by the 28:

- Timestamps are already Bangkok local time → `parseFlexibleDatetime` (not the UTC variant).
- Date-only columns that are always `'YYYY-MM-DD 00:00:00'` → `DATE(parseFlexibleDatetime(col))`:
  `quotation_date` in the 6 `crm_quotation*` tables, `crm_sale_order.po_expire_date`,
  `crm_sale_order_attachment.expiry_date`, `crm_sale_order_deposit.due_date`,
  `sales_customer_sales_territory.start_date` / `end_date`, `sales_employee_sale_territory.end_date`.
- Columns sent as bare `'YYYY-MM-DD'` → `parseFlexibleDate` (DATE; `parseFlexibleDatetime` would
  return NULL): `crm_nd_sd_price.effective_from` / `expiry_to`, `crm_sale_order.next_due_date` /
  `po_date`, `sales_sales_territory.valid_from` / `valid_to`.
- `time_start` / `time_end` (`'HH:MM:SS'`, delivery tables) stay strings. AVRO `boolean`
  columns are kept as is; `double` → `castFloat64`, `int` → `castInt64`.
- Dedup `ORDER BY updated_at DESC, asatdate DESC`; tables with no `updated_at`
  (`crm_sale_order_approval_log`, `crm_sale_order_approver`, `crm_sale_order_payment_allocation`,
  `crm_sale_order_status_history`) order by `created_at`. Rows deleted at source are not purged.

**Customer / business-unit tables (10, all incremental, added 2026-10-29)** —
all use `ASATDATE` partitions. All 12 AVRO files in `ASATDATE=20261029` were checked
(three address shards have identical schemas); query-time external SELECTs confirmed
all keys below are unique and nonblank after trimming. One partition cannot prove ID
stability across resyncs or the future feed cadence.

| Table | PK | First-partition rows | AVRO columns |
|---|---|---:|---:|
| `crm_business_unit` | `business_unit_id` | 141 | 39 |
| `crm_customer_address` | `customer_address_id` | 81,218 | 29 |
| `crm_customer_contact` | `customer_contact_id` | 22,567 | 19 |
| `crm_customer_contact_channels` | `customer_contact_channels_id` | 12 | 14 |
| `crm_customer_credit` | `customer_credit_id` | 22,529 | 24 |
| `crm_customer_data_zone` | `customer_data_zone_id` | 8 | 26 |
| `crm_customer_master` | `customer_master_id` | 22,547 | 54 |
| `crm_customer_segment` | `customer_segment_id` | 22,518 | 25 |
| `crm_customer_stores` | `customer_stores_id` | 6,309 | 20 |
| `crm_data_zone` | `data_zone_id` | 4 | 18 |

- All actual AVRO fields are retained, plus `asatdate`. `crm_customer_contact_channels`
  and `crm_customer_stores` preserve `status`; the workbook-only `is_active` is not invented.
- `crm_business_unit` has six effective/expiry dates; `crm_customer_credit` has
  `credit_limit_change_date`, `collateral_start_date`, `collateral_end_date`.
  Use `parseFlexibleDate`: populated values are bare `YYYY-MM-DD`; expiry/collateral
  fields currently all NULL retain the workbook DATE contract.
- `created_at` / `updated_at` use `parseFlexibleDatetime` without a timezone shift,
  consistent with CRM siblings. Customer timestamps later than upload's UTC clock
  support the local-time interpretation; unit/zone timezone is not independently
  established. The existing helper truncates fractional seconds to seconds.
- Dedup orders by `updated_at DESC, asatdate DESC`. For `crm_business_unit`,
  `crm_customer_data_zone`, `crm_data_zone`, nullable updates fall back to
  `COALESCE(updated_at, created_at) DESC, asatdate DESC`.
- `crm_customer_stores.created_at` contains a source value in year 2569. It is retained
  as supplied, not silently converted between calendars; dedup uses `updated_at`.
- AVRO booleans use `castBool`, integers `castInt64`, doubles `castFloat64`; string
  keys use `IFNULL(cleanString(...), '')`. No hard-delete purge is added.

**Combo-set, payment, formula and price-sync tables (10, all incremental)** —
the seven CRM combo-set/payment tables and three inventory tables added after the
previous 41 DERP tables.

| Table | PK | AVRO columns |
|---|---|---:|
| `crm_combo_set` | `combo_set_id` | 14 |
| `crm_combo_set_customer` | `combo_set_customer_id` | 9 |
| `crm_combo_set_item` | `combo_set_item_id` | 18 |
| `crm_combo_set_sale_territory` | `combo_set_sale_territory_id` | 13 |
| `crm_master_payment_condition` | `master_payment_condition_id` | 14 |
| `crm_master_payment_method` | `master_payment_method_id` | 17 |
| `crm_master_payment_term` | `master_payment_term_id` | 16 |
| `inventory_formula_line` | `formula_line_id` | 62 |
| `inventory_formula_versions` | `formula_versions_id` | 36 |
| `sync_mac5_inventory_item_price` | `inventory_item_price_id` | 25 |

- `crm_combo_set`, `crm_combo_set_customer`, `crm_combo_set_item` and
  `crm_combo_set_sale_territory` use the Excel data-dictionary PKs. Their declared
  references include audit user IDs, combo-set IDs, customer IDs, product IDs and
  sales-territory IDs.
- The three payment tables use their Excel data-dictionary PKs and reference `users(id)`
  through creator/updater IDs. Formula-table keys also come from the data dictionary.
  Formula lines reference `formula_versions.formula_id` and `products.item_number`;
  `formula_versions_id` is a candidate direct link to `formula_versions_id`. Both
  formula tables carry product identifiers; their D365 timestamp strings use the UTC parser.
- Formula date strings use `parseFlexibleDate`; their AVRO string flags become booleans
  using the documented Y/N or Yes/No source values.
- CRM timestamps use `parseFlexibleDatetime`, consistent with CRM siblings.
  Combo-set start/end dates use `parseFlexibleDate`.
- `sync_mac5_inventory_item_price` uses the sibling `inventory_item_price_id` key and
  incremental load pattern. Its timestamp and active/price flags follow the existing
  `inventory_item_price` definition; source-timezone interpretation remains unconfirmed.
- The seven combo-set/payment PKs and both formula PKs are the source keys marked PK in
  the Excel data dictionary. One `ASATDATE=20261105` partition was observed per feed;
  file listing metadata alone does not show whether any partition is a complete snapshot
  or only changes. No row-level key uniqueness scan was run for these new feeds.

**Additional CRM tables (5, all incremental, added 2026-11-09)** — schema columns from
the delivered AVRO files; each uses its source ID as the validated key.

| Table | PK | AVRO columns |
|---|---|---:|
| `crm_customer_bank_account` | `customer_bank_account_id` | 15 |
| `crm_customer_branch` | `customer_branch_id` | 54 |
| `crm_nd_sd_price_channel` | `nd_sd_price_channel_id` | 11 |
| `crm_quotation_terr_cust` | `quotation_terr_cust_id` | 29 |
| `crm_quotation_terr_sale` | `quotation_terr_sale_id` | 30 |

- Delivery status: all five `ASATDATE=20261109/<table>_20261109_000.avro` files
  contain schemas with zero rows. D-ERP confirmation of whether the source is actually
  empty is pending; this delivery does not establish the future feed cadence.
- CRM timestamps use `parseFlexibleDatetime` without a timezone shift, matching CRM siblings.
  `quotation_date` is a midnight timestamp stored as DATE. AVRO booleans, doubles and
  integers use `castBool`, `castFloat64` and `castInt64`; other source strings use
  `cleanString`. String keys are made non-null with `IFNULL(cleanString(...), '')`.
- The source ID fields above are used as primary keys; no composite key or document purge
  is added.

The first build of every DERP table dedups by ID across all raw partitions (for the
journals, this includes the initial 3-day full load). Incremental runs read only the `BACKFILL_DAYS` window,
dedup that input, then MERGE by ID; they do not rescan all historical partitions.

Direct downstream readers are listed in the [validated DERP table cards](../../okf/validated/validated_derp/index.md).
Source context: [source-systems § DERP](../overview/source-systems.md#derp--inventory).

## ALLKONS_COMMISSION — ⚠️ **ถูก pause แล้ว ไม่มีไฟล์ validated เหลือเลย**

> commit `74a10e0 "pause process data layer of commission"` ลบ
> `definitions/validated/allkons_commission/` ทิ้งทั้งโฟลเดอร์ (เดิม 8 ไฟล์)
> · raw external table 7 ตัวยังถูกสร้างอยู่ที่ชั้น initial · dataset
> `validated_allkons_commission` ยังค้างข้อมูลเก่าใน BigQuery แต่ไม่มีใครเติม
> และไม่มีอะไร downstream ใช้
>
> ข้อมูลข้างล่างเก็บไว้เผื่อรื้อฟื้น — อย่าอ่านว่าเป็น inventory ของปัจจุบัน

ตอนที่ยังใช้งาน (8 = 7 incremental + 1 schema) — PK `id`

Sales-commission source, added 2026-08-18. GCS prefix `allkons_commission/`,
one folder per table, Hive-partitioned by `ASATDATE=` like every other source.

| Table | What it holds |
|---|---|
| `mac5_transactions` | order/invoice/receipt lines with payment + commission fields (largest — 931k rows in the 2026-08-06 snapshot) |
| `mac5_sales_areas` | sales areas, links to `mac5_sales_channel_id` |
| `mac5_sales_channels` | sales channels, links to `sales_channel_id` |
| `sales_channels` | channel master |
| `sales_positions` | position master |
| `marketing_condition_version_details` | versioned commission conditions |
| `target_commission_monthly_carries` | monthly target carry-over per sales id |

All 7 follow the standard validated pattern exactly: `type: "incremental"`,
tags `validated` + `validated_incremental`, `partitionBy: "asatdate"`,
`clusterBy: ["id"]`, the `BACKFILL_DAYS` window, QUALIFY dedup and the PK
post-operation. `uniqueKey` is `["id"]` on every table — **verified against the raw
AVRO on 2026-08-18**: `id` is unique in every snapshot, including
`marketing_condition_version_details` (45/45) and `mac5_transactions` (931,173/931,173).

Two gotchas worth keeping:

- `mac5_sales_areas` and `mac5_sales_channels` select a column literally named
  `desc`, a GoogleSQL reserved word. It **must** be backtick-quoted inside the
  helper — `cleanString('\`desc\`')`. Without the backticks BigQuery fails with
  `Syntax error: Expected ")" but got keyword DESC`.
- The 2026-08-02 partition contains the same snapshot loaded 3–4 times
  (`mac5_sales_channels` 272 rows / 68 distinct, `sales_positions` 12 / 4) — a
  test re-run by the data team. The rows are byte-identical, so QUALIFY collapses
  them correctly; no action needed.

The GCS prefix also holds a `mac5_transactions_view/` folder that is deliberately
**not** declared as an external table (decision 2026-08-18).

Nothing downstream reads `validated_allkons_commission` yet.

## Schema-bootstrap files (6)

ทุก source มีไฟล์ `validated_schema_<source>.sqlx` อยู่ 1 ตัว — `type: "operations"`
ทำหน้าที่ `CREATE SCHEMA IF NOT EXISTS` และเป็นตัวที่ตาราง curated ของ source นั้นไปผูก dependency ถึง
นับรวมในตัวเลขของแต่ละ source ข้างบนแล้ว:

| File | Source |
|---|---|
| `validated_schema_mac5.sqlx` | MAC5 |
| `validated_schema_cis360.sqlx` | CIS360 |
| `validated_schema_mastersku.sqlx` | MASTERSKU |
| `validated_schema_master_sku.sqlx` | MASTER_SKU |
| `validated_schema_saleout.sqlx` | SALEOUT_MDT |
| `validated_schema_derp.sqlx` | DERP |

ไม่มี `validated_schema_allkons_commission.sqlx` แล้ว — ดูหัวข้อ ALLKONS ข้างบน

**รวมทั้งชั้น**: จำนวนไฟล์ล่าสุด (นับรวม schema-bootstrap ของแต่ละ source) ดูที่
[generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview)

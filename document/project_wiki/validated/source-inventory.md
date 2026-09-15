# Validated Layer — Source Inventory

> **LLM context**: Table-level inventory per source. Descriptions of MAC5 3-letter
> codes are inferred from column prefixes — verify in-file when it matters.
> Authoritative full-load list: `grep -l 'TAG_VALIDATED_FULL' definitions/validated/mac5/`.

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

## SALEOUT_MDT (12 = 11 incremental + 1 schema) — by retailer subfolder

| Folder | Tables |
|---|---|
| `BT/` | `sales_by_branch`, `sale_by_branch_detail`, `sale_by_branch_mch3`, `stock_by_branch`, `stock_aging`, `turnover`, `turnover_brand` |
| `GB/` | `saleout_gb` |
| `HP/` | `saleout_hp` |
| `TW/` | `report_sale_subscription` |
| `LASTYEAR/` | `saleout_lastyear` — ไฟล์ Excel ย้อนหลังก่อนที่ TW จะส่ง feed (เพิ่ม 2026-09) |

All `type: "incremental"` but tagged only `validated`; PKs are wide business
composites (e.g. `["sale_no","sale_date","branch_code","product_code"]`).

**2026-08-17** — all 10 (ตอนนั้น) were brought onto the standard validated pattern: they gained
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

Nothing downstream reads `validated_saleout_mdt` — no curated, dimension, fact or
view references it. The layer ends here and is consumed directly by BI.

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

## Schema-bootstrap files (4)

ทุก source มีไฟล์ `validated_schema_<source>.sqlx` อยู่ 1 ตัว — `type: "operations"`
ทำหน้าที่ `CREATE SCHEMA IF NOT EXISTS` และเป็นตัวที่ตาราง curated ของ source นั้นไปผูก dependency ถึง
นับรวมในตัวเลขของแต่ละ source ข้างบนแล้ว:

| File | Source |
|---|---|
| `validated_schema_mac5.sqlx` | MAC5 |
| `validated_schema_cis360.sqlx` | CIS360 |
| `validated_schema_mastersku.sqlx` | MASTERSKU |
| `validated_schema_saleout.sqlx` | SALEOUT_MDT |

ไม่มี `validated_schema_allkons_commission.sqlx` แล้ว — ดูหัวข้อ ALLKONS ข้างบน

**รวมทั้งชั้น: 136 ไฟล์** = MAC5 87 + CIS360 25 + MASTERSKU 12 + SALEOUT_MDT 12
(นับรวม schema-bootstrap ของแต่ละ source แล้ว) · ตรวจ 2026-09-15

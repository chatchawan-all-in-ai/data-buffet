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

## SALEOUT_MDT (12 = 7 incremental + 4 full + 1 schema) — by retailer subfolder

| Folder | Tables | Materialization |
|---|---|---|
| `BT/` | `sale_by_branch_detail`, `sales_by_branch`, `sale_by_branch_mch3`, `turnover`, `turnover_brand` | incremental |
| `BT/` | `stock_by_branch`, `stock_aging` | **table (full)** — 2026-09-15 |
| `GB/` | `saleout_gb` | incremental |
| `HP/` | `saleout_hp` | incremental |
| `TW/` | `report_sale_subscription` | **table (full)** — 2026-09-14 |
| `LASTYEAR/` | `saleout_lastyear` | **table (full)** — 2026-09-11, one-off Excel |

PKs on the incremental nine are wide business composites
(e.g. `["sale_no","sale_date","branch_code","product_code","row_no"]`).

**2026-08-17** — the original 10 were brought onto the standard validated pattern: they
gained `partitionBy: "asatdate"` (they had `clusterBy` only, the single group in the whole
layer without a partition) and the incremental
`${when(incremental(), \`WHERE ASATDATE >= …BACKFILL_DAYS…\`)}` window, which they had
never had. Before that, every run rescanned the full raw history — ~1.2 GB/night to
produce ~80k rows, with `report_sale_subscription` alone at 721 MB.

The window is safe for the incremental nine: all 858 raw objects across the four retailer
folders (`hp` 84, `gb` 82, `tw` 84, `bt` 608) were uploaded on the same day as their own
`ASATDATE=` partition — **zero back-dated files** — so no vendor correction older than
`BACKFILL_DAYS` has ever arrived. If a retailer ever starts resending history, raise
`BACKFILL_DAYS` for that run instead of removing the window.

### Two tables are full loads on purpose

Both sources are **snapshots with no row-level key**, so any MERGE key either drops rows
or duplicates them. Full reload sidesteps the problem; both are small enough that
re-reading GCS nightly is cheaper than the code needed to get a MERGE key right.

`report_sale_subscription` (TW) — converted 2026-09-14. Its `uniqueKey` was
`(Store, Cat, Sub_Cat, Brand, SKU)` with **no `ASATDATE`**, so each night's MERGE
overwrote the previous day's snapshot in place (the MERGE also rewrites the partition
column). Measured: raw 1,552,616 rows / 109 feed days → validated held **9,816 rows**,
a 99.4% loss, effectively one snapshot. Adding `ASATDATE` to the key was rejected because
the remaining key columns are nullable — `Store` empty on 354 rows, `SKU` on 531, the
per-file `Description = 'Total'` summary rows — and a NULL in a MERGE key never matches,
so those rows would re-INSERT every night. No `QUALIFY` either: the first file
(`ASATDATE=20260513`, 546,194 rows) is a ~59-snapshot backlog dump whose rows are only
separable by `Last_Sold_Date`, so deduplication belongs in curated, not here.

`saleout_lastyear` — one-off Excel, 6,968 rows collide on the curated key with no line
discriminator to split them; collapsing at this layer would lose money.

`stock_by_branch` / `stock_aging` (BT) — converted 2026-09-15, same bug as TW. Their
`uniqueKey` had neither `ASATDATE` nor `end_date`, so each night's MERGE overwrote the
previous snapshot. Measured: raw 41,286 / 43,088 rows over 114 feed days → validated held
**384 and 1,065 rows** (99.1% and 97.5% lost). Adding `end_date` to the key is not enough
either — one file carries several periods (167 distinct `END_DATE` from 114 file days), so
a 1-day incremental window cannot keep up. Unlike TW these **do** need deduplication: every
duplicate group is byte-identical (1,982 and 2,134 groups), and keeping them would double
stock quantities on `SUM`. So: full load + `QUALIFY` on business key + `end_date` + `asatdate`.
After the fix: **39,048 and 40,675 rows over 114 days**.

⚠️ The other four BT tables (`sales_by_branch`, `sale_by_branch_mch3`, `turnover`,
`turnover_brand`) have the **same bug and are still broken** — 2,694→19, 1,406→13,
3,077→17, 3,305→19 rows. Left alone deliberately: nothing reads them yet. Fix them the
same way before any consumer appears.

### `saleout_hp` แยกห้างด้วยตัวอักษรแรกของ `SITENO` (แก้ 2026-09-14)

ไฟล์เดียวมี 2 ห้าง — `S…` = HP · `M…` = MH · prefix อื่นได้ NULL โดยเจตนา เพื่อให้
ตรวจเจอรหัสใหม่ที่ยังไม่รู้จัก

⚠️ กฎนี้ผิดกับ 3 รหัส ต้องระบุตรง ๆ: `M888` ขึ้นต้น M แต่เป็น "บมจ. โฮมโปรดักส์
เซ็นเตอร์" = HP สำนักงานใหญ่ · `CS01` = HP รังสิต-ปทุมธานี · `EX99` = HP Inter
Company (สองตัวหลังเดิมได้ NULL) รวม **20 แถว / 168,646.50 บาท** ที่เคยจับ
`BranchMdtSK` ไม่ได้ ยืนยันจากไฟล์ Excel ย้อนหลังของ BI ที่ติดป้าย `M888` เป็น HP

ตรวจ 2026-09-14 หลังแก้: รหัสสาขาในฟีด 137 ตัว — dim มีครบ 137 · ห้างตรงกัน 137 ·
`store_code IS NULL` เหลือ 0 แถว จาก 38,303

⚠️ ยังเป็นการเดาอยู่ ทางที่ทนกว่าคือขอให้ห้างส่งรหัสห้างมาในไฟล์ · ระหว่างนี้มี
query เฝ้าใน `document/operations/known-issues.md`

### Downstream

`curated_saleout_mdt` reads `saleout_hp`, `sale_by_branch_detail` (BT), `saleout_gb`,
`report_sale_subscription` (TW, added 2026-09-14) and `saleout_lastyear`;
`fact_saleout_mdt` reads the curated table.

`curated_stock_mdt` (added 2026-09-15) reads `stock_by_branch` (BT) and
`report_sale_subscription` (TW) → `fact_stock_mdt` → `fact_stock_mdt_monthly`.

`stock_aging` and the four remaining BT tables still have no consumer.

## ALLKONS_COMMISSION (8 = 7 incremental + 1 schema) — PK `id`

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

# Process Layer — `definitions/process/`

> **LLM context**: 2 files with tag `process`, plus the Pub/Sub export pilot
> (4 `.sqlx` + 1 `.js` here, plus the export view in `definitions/view/pub_sub/`;
> tag `run_log_daily`, see the last section).
> 1. **`deb_address_data.sqlx`** — AI-powered Thai address parsing, gated on CDC so only
>    *changed* addresses are re-parsed each day. Writes to `process_dataset.deb_address_data`;
>    the companion view `process_dataset.view_deb_address_data` is what `fact_transcation`
>    and `dim_customer` consume for Province/District/SubDistrict SKs.
> 2. **`rls_customer360.sqlx`** — per-customer access map for **row-level security**
>    on Customer360 (see the section at the bottom). Plain `type: "table"`, no AI.

## Config

- `type: "incremental"`, schema `process_dataset`, tag `process`
- `uniqueKey: ["company_id", "debcode"]`, `clusterBy` same (partition commented out)
- No declared `dependencies`, but **functionally gated on `cdc_dataset.cdc_change_log`**

## What it does

1. Reads `validated_mac5.deb`, concatenates `debadd1at + debadd2at + debadd3at`
   into `raw_address`.
2. Calls BigQuery **`AI.GENERATE(...)`** with model endpoint `gemini-3.5-flash-lite`
   (temperature 0.1) and a Thai "Expert Thai Geographic Data Extractor" prompt.
3. Output struct `info`: `SubDistrictTH, SubDistrictEN, DistrictTH, DistrictEN,
   ProvinceTH, ProvinceEN`.

## CDC gating (the cost control)

```sql
WHERE EXISTS (
  SELECT 1 FROM cdc_dataset.cdc_change_log
  WHERE source_system = 'mac5'
    AND source_schema = 'validated_mac5'
    AND source_table  = 'deb'
    AND asatdate = CURRENT_DATE('Asia/Bangkok')
    AND JSON_VALUE(pk_fields, '$.debcode') = deb.debcode
    AND IFNULL(JSON_VALUE(pk_fields, '$.company_id'), 'ag01') = deb.company_id
)
```

Only customers whose address changed **today** (per CDC) hit the LLM — everything
else keeps its previously parsed value. Blank addresses are skipped.

## Why this matters

`AI.GENERATE` costs per call. Without CDC gating, every daily run would re-parse the
entire customer master. This is the reference example for "expensive derivation +
CDC gate" — reuse this pattern for any future LLM/UDF-heavy enrichment.

---

## `rls_customer360.sqlx` — row-level-security access map

`type: "table"` in `process_dataset`, tag `process`,
`dependencies: ["fact_transcation", "dim_region", "dim_section", "dim_director", "dim_product_mkt"]`.

> 2026-08-11: ไฟล์นี้เคยเขียน path เป็น `databuffet-nonprd.…` ตรงๆ 5 จุด และไม่มี `js`
> block เลย — เปลี่ยนมาใช้ `js` ref ตามมาตรฐาน (`databuffet.DATABASE` +
> `databuffet.FACT_TABLE`/`DIMENSION_TABLE`) และประกาศ dim ทั้ง 4 ตัวใน
> `dependencies[]` ตามไปด้วย SQL ที่ compile ออกมาเหมือนเดิมทุกตัวอักษร
Builds **one row per customer** (`milCus`) listing every sales entity associated with
that customer, so downstream row-level security can decide who may see a customer.

For each `milCus` it `STRING_AGG(DISTINCT …, '|')`s (pipe-delimited) over
`fact_transcation` joined to the dims:

| Column | Source | Meaning |
|---|---|---|
| `milPer` | fact | sales-person id(s) |
| `SectionID` | `dim_section` (via `SectionSK`) | section(s) |
| `RegionID` | `dim_region` (via `RegionSK`) | region(s) |
| `DirectorID` | `dim_director` (via `DirectorSK`) | director(s) |
| `ProductMkt` | `dim_product_mkt` (via `ProductMktSK`) | `MarketingGroupID:SubMarketingID:SegmentID` combo(s) |

No AI, no CDC gate — a straight daily rebuild off `fact_transcation`, so it inherits
that fact's coverage. The `CREATE OR REPLACE TABLE` header is commented out because
Dataform materializes it from the `config` block. RLS is also referenced in
[operations/known-issues.md](../../operations/known-issues.md) and
[architecture/overview.md](../../architecture/overview.md).

---

## Pub/Sub export pilot — `dim_company` (2026-10-24)

The repository half of "Data Mart → Pub/Sub": Dataform logs the start and end of the
`daily_process` run and keeps an export view per exported table. A Cloud Workflow
(not in this repo; built after merge) will compare each export view with the sent
state and publish changed rows. The planned GCP setup and message format are owned by
[setup-pubsub-export.md](../../how-to/setup-pubsub-export.md).
Only `dim_company` in `databuffet-nonprd` and only the `daily_process` run for now; start/end logging for
`saleout_morning` and `yearly_process` comes later.

Bookkeeping tables live in `process_dataset`; every view read by Pub/Sub lives in its
own dataset `pub_sub` (`databuffet.PUB_SUB`, file under `definitions/view/pub_sub/`).
Every action carries tag `run_log_daily` (`databuffet.TAG_RUN_LOG_DAILY`):

| File | Builds | What |
|---|---|---|
| `mart_process_log.sqlx` | `process_dataset.mart_process_log` | `CREATE TABLE IF NOT EXISTS` — one row per run: `run_id`, `process_name`, `status` (`STARTED`/`FINISHED`), `started_at`, `finished_at`, `publish_claimed_at`, `published_at` (UTC). Never rebuilt |
| `mart_process_start.sqlx` | operation | `INSERT` a `STARTED` row with a new `run_id` |
| `mart_process_end.js` | operations `mart_process_end` + `mart_process_barrier_*` | End: `UPDATE` the latest `STARTED` row of its `process_name` to `FINISHED` + `finished_at`; never touches `publish_claimed_at` / `published_at` (the workflow owns them). Barriers: no-op `SELECT 1`, see below |
| `mart_sent_state.sqlx` | `process_dataset.mart_sent_state` | `CREATE TABLE IF NOT EXISTS` — `table_name`, `row_key`, `row_hash`, `run_id`, `sent_at`, cluster `table_name, row_key`. Only the workflow writes it, after a publish succeeds |
| `mart_export_config.sqlx` | `process_dataset.mart_export_config` (table) | One row per exported table — `table_name`, `process_name`, `source_view`, `topic` — generated from `includes/controller/mart-export-config.json` |
| `pub_sub/pub_sub_schema.sqlx` | dataset `pub_sub` | `CREATE SCHEMA IF NOT EXISTS ... OPTIONS(location=REGION)`, the same bootstrap as `validated_schema_*` / `cdc_schema`. `definitions/pub_sub/` is the layer folder for future shaping tables before Pub/Sub |
| `view/pub_sub/export_dim_company.sqlx` | `pub_sub.export_dim_company` (view, tags `view` + `run_log_daily`) | `company_source_id` (= `CompanyID`), `CompanyCode`, `CompanyNameTH`, `CompanyNameEN`, `row_key`, `row_hash` — no `CompanySK`, no `MdsId` |

**"End waits for the whole run."** `mart_process_end` runs after every action that
carries one of `run_tags` in `mart-export-config.json`, excluding itself and its
barriers. Dependencies are selected at compile time and grouped behind no-op
barriers, so new actions under those tags are covered automatically without
exceeding the dependency limit. The compiler constraint and upgrade checks are in
[known issues](../../operations/known-issues.md#mart_process_end-สร้าง-dependency-ตอน-compile-2026-10-24).
Any failed action skips the end: the row stays `STARTED` and is ineligible for
publishing. A repair run inserts a new row and its end closes that row.

The future publisher selects `FINISHED` runs with no `published_at`, claims a run
using `publish_claimed_at` before sending to prevent overlapping sends, and sets
`published_at` only after every configured table has been sent. It compares each
export view with `mart_sent_state`: absent key = `NEW`, different hash = `UPDATE`,
key only in state = `DELETE`. State represents the rows receivers currently hold;
only the publisher updates it after successful sends.

**Export view contract** (every export view):

- data columns first, `company_source_id` first of all; no SK of any dimension and no
  value that moves by itself day to day — otherwise every row looks changed every day;
- `row_key = TO_JSON_STRING(STRUCT(<natural key>))` — becomes `primary_key`, never NULL;
- `row_hash = FARM_FINGERPRINT(TO_JSON_STRING(<all data columns>))` — the fingerprint of
  exactly the message `data`, so it changes only when something sent changes. Strings
  go through `cleanString`; round decimals to a fixed scale before they reach the hash.

`dim_company`'s key is `company_source_id` + `CompanyCode` (the pair its MERGE
matches on). Checked 2026-10-24 with time travel: `row_hash` of all 5 rows is identical
across the snapshots after the 2026-10-22, 10-23 and 10-24 runs.

**Add a table to the export:** add an `export_<table>.sqlx` view in
`definitions/view/pub_sub/` (schema `databuffet.PUB_SUB`, tags `TAG_VIEW` +
`TAG_RUN_LOG_DAILY`, `dependencies` including `pub_sub_schema`) following the contract, then one entry under `tables` in `mart-export-config.json` (`table_name` =
the message `table`, `source_view`, `topic`). The workflow reads
`mart_export_config` and needs no change; the topic and subscriptions are created on
the GCP side.

**Enable in Dataform:** follow the
[schedule reference](../operations/running-and-troubleshooting.md#schedule-dataform-service-databuffet-nonprd)
for the UI tag change and keeping `run_tags` aligned. `pub_sub_schema` creates its
dataset in `databuffet.REGION` on the first execution; the view depends on it.
Running a single mart table or export view without the logging actions creates no
publishable run. Publishing itself remains post-merge GCP work.

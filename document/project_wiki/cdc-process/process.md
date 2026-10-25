# Process Layer — `definitions/process/`

> **LLM context**: 2 files with tag `process`, plus the Pub/Sub export pilot
> (2 `.sqlx` here, plus `definitions/pub_sub/pub_sub_schema.sqlx` and the export view
> in `definitions/view/pub_sub/`; tag `pub_sub`, run by hand — see the last section).
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

The repository half of "Data Mart → Pub/Sub": Dataform keeps an export view per
exported table plus two bookkeeping tables. A Cloud Workflow (not in this repo; built
after merge) will read run status from the **Dataform API**, compare each export view with
the sent state and publish changed rows. The planned GCP setup and message format are
owned by [setup-pubsub-export.md](../../how-to/setup-pubsub-export.md).
Only `dim_company` in `databuffet-nonprd` for now.

**Run status comes from the Dataform API, not from Dataform actions** (redesigned
2026-10-25). There are no start/end actions and no per-run log table. The publisher
will discover scheduled and manual runs with `workflowInvocations.list`. Each
[`WorkflowInvocation`](https://docs.cloud.google.com/dataform/reference/rest/v1/projects.locations.repositories.workflowInvocations)
provides `workflowConfig` (a resource name ending in `workflowConfigs/<scheduler>`;
unset = manual), `state`, and `invocationTiming.startTime` / `endTime`.
Selected tags are in
[`invocationConfig.includedTags`](https://docs.cloud.google.com/dataform/reference/rest/v1/InvocationConfig)
when present; target-selected and whole-workflow runs need not have tags. Use
[`workflowInvocations.query`](https://docs.cloud.google.com/dataform/reference/rest/v1/projects.locations.repositories.workflowInvocations/query)
to check actual action targets and their states. Adding a scheduler or running by
hand needs no change in Dataform or in the Dataform UI.

Bookkeeping tables live in `process_dataset`; every view read by Pub/Sub lives in its
own dataset `pub_sub` (`databuffet.PUB_SUB`, file under `definitions/view/pub_sub/`).
Every action carries tag `pub_sub` (`databuffet.TAG_PUB_SUB`), which **no scheduler
runs** — see "Deploy" below:

| File | Builds | What |
|---|---|---|
| `mart_export_config.sqlx` | `process_dataset.mart_export_config` | One row per exported table. `CREATE TABLE IF NOT EXISTS`, then an insert-only `MERGE` from `includes/controller/mart-export-config.json`. Columns below |
| `mart_sent_state.sqlx` | `process_dataset.mart_sent_state` | One row per data row sent. `CREATE TABLE IF NOT EXISTS`, cluster `table_name, row_key`. Columns below. Only the workflow writes it, after a publish succeeds |
| `pub_sub/pub_sub_schema.sqlx` | dataset `pub_sub` (tags `view` + `pub_sub`) | `CREATE SCHEMA IF NOT EXISTS ... OPTIONS(location=REGION)`, the same bootstrap as `validated_schema_*` / `cdc_schema`. `definitions/pub_sub/` is the layer folder for future shaping tables before Pub/Sub |
| `view/pub_sub/export_dim_company.sqlx` | `pub_sub.export_dim_company` (view, tags `view` + `pub_sub`) | `company_source_id` (= `CompanyID`), `CompanyCode`, `CompanyNameTH`, `CompanyNameEN`, `row_key`, `row_hash` — no `CompanySK`, no `MdsId` |

`mart_export_config` (times UTC):

| Column | Owner | Meaning |
|---|---|---|
| `table_name` | Dataform (JSON, on insert) | Exported table = the message `table`; also the Dataform action whose run triggers an export |
| `source_view` | Dataform (JSON, on insert) | Full name of the export view (`databuffet-nonprd.pub_sub.export_<table>`) |
| `topic` | Dataform (JSON, on insert) | Pub/Sub topic |
| `last_invocation_id` | workflow | Memory: the last Dataform workflow invocation already handled for this table |
| `last_invocation_end` | workflow | End time of that invocation; `NULL` before the first export, then only invocations that ended later are new |
| `claimed_at` | workflow | Being-processed marker; `NULL` = free |

The `MERGE` only inserts new export tables. Every existing row is preserved, including
`source_view`, `topic`, `last_invocation_id`, `last_invocation_end` and `claimed_at`,
even if its JSON entry changes or is removed. Changing an existing export table's
view/topic or removing it is a deliberate manual change. `ref()` to each export view
keeps a config row naming a missing view a compile error.

`mart_sent_state`: `table_name`, `row_key` (the table's natural key), `row_hash`
(fingerprint of the row data), `invocation_id` (the Dataform workflow invocation that
sent it), `sent_at` (UTC). It holds the last successfully recorded state; a row matching
its stored `row_key` + `row_hash` is skipped.

**Duplicate guard** (contract for the future workflow, polled every 5 minutes). For
each row of `mart_export_config` the workflow must:

1. Ask the Dataform API for the newest `SUCCEEDED` invocation whose actions include
   `table_name` with state `SUCCEEDED`, and whose end time is later than
   `last_invocation_end` (or any end time when that checkpoint is `NULL`). None →
   stop for this table **without reading `mart_sent_state`**. Log the scheduler id
   from `workflowConfig` (unset = manual) with the invocation id.
2. Claim the row atomically: `UPDATE mart_export_config SET claimed_at = CURRENT_TIMESTAMP()
   WHERE table_name = ... AND (last_invocation_end IS NULL OR last_invocation_end < <end_time>) AND claimed_at IS NULL`
   (plus a timeout for an abandoned claim, set with the workflow). 0 rows updated →
   another run holds it or already handled this or a newer invocation → stop.
3. Diff the export view with `mart_sent_state`, reading only `row_key`, `row_hash`
   `WHERE table_name = ...`: absent key = `NEW`, different hash = `UPDATE`, key only in
   state = `DELETE`; equal hash = not sent.
4. Publish, then `MERGE` only the sent rows of that `table_name` into
   `mart_sent_state` (`invocation_id` = the invocation) and delete the `DELETE`d keys.
5. Set `last_invocation_id`, `last_invocation_end` and `claimed_at = NULL`. If it
   fails before this step, the memory is unchanged and the next run retries; rows
   already recorded in `mart_sent_state` are not sent again.

Several new invocations since the last one are handled as one: the diff compares the
current view, so only the newest matters.

Publishing and recording sent state are separate operations: a failure between
them can resend a row on retry. Receivers must follow the idempotency and delivery
rules in the [message guide](../../how-to/setup-pubsub-export.md).

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
`TAG_PUB_SUB`, `dependencies` including `pub_sub_schema`) following the contract, then
one entry under `tables` in `mart-export-config.json` (`table_name` = the message
`table` and the Dataform action that triggers it, `source_view`, `topic`), then run
tag `pub_sub` once as below. The workflow needs no change; the topic and
subscriptions are created on the GCP side. For existing exports, the insert-only
config lifecycle above applies.

### Deploy

Run by hand, with no workflow configuration change. Once the code reaches `nonprod`,
follow these steps for the first deployment and whenever an export table is added:

1. In Dataform → Releases & Scheduling → release config `production`, select
   **New compilation** and wait for success, or verify that its existing live
   compilation's commit SHA includes the change on `nonprod`.
2. Verify the successful result is live and its commit includes the change, then
   run tag `pub_sub` from `production` with **include dependencies off**.

Manual execution uses the release's live compilation result
([Dataform compilation reference](https://docs.cloud.google.com/dataform/docs/configure-compilation#trigger-execution-release-configuration)).
The run creates the `pub_sub` dataset (in `databuffet.REGION`), the export views and
the two tables, and only adds missing export config rows. Re-running preserves every
existing config row, the memory and the sent state. No workflow configuration carries
`pub_sub`. Do not use tag `view` for this: it deploys every view and skips the two
tables. Publishing itself remains post-merge GCP work.

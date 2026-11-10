# Process Layer — `definitions/process/`

> **LLM context**: 2 files with tag `process`, plus the Pub/Sub export publisher
> (2 `.sqlx` here, plus `definitions/pub_sub/pub_sub_schema.sqlx` and the export views
> in `definitions/view/pub_sub/`; tag `pub_sub`, run by hand — see the last section).
> TA customer access is also built in this folder; see [`rls_ta_customer`](#rls_ta_customersqlx--ta-customer-access-who-sees-which-customer).
> 1. **`deb_address_data.sqlx`** — AI-powered Thai address parsing, gated on CDC so only
>    *changed* addresses are re-parsed each day. Writes to `process_dataset.deb_address_data`;
>    the companion view `process_dataset.view_deb_address_data` is what `fact_transcation`
>    and `dim_customer` consume for Province/District/SubDistrict SKs.
> 2. **`rls_customer360.sqlx`** — per-customer access map for **row-level security**
>    on Customer360 (see the section at the bottom). Plain `type: "table"`, no AI.
>
> The Pub/Sub publisher itself is a pair of Cloud Run jobs kept in `pubsub/` (not Dataform).

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

## Pub/Sub export

"Data Mart → Pub/Sub": Dataform keeps an export view per exported table plus two
bookkeeping tables. The publisher is two Cloud Run jobs in `us-central1`, one program
([`pubsub/publisher/main.py`](../../../pubsub/publisher/main.py), modes `check` and `send`):
Cloud Scheduler `datamart-publish-check-every-5m` runs the **check job** `datamart-publish-check`
every 5 minutes; it reads run status from the **Dataform API** and, when a table has a new
run to export, starts the **send job** `datamart-publish-send`, which compares each export view
with the sent state and publishes the changed rows. The diff query is
[`pubsub/sql/diff.sql`](../../../pubsub/sql/diff.sql), shared with the first-load script.
Diff rows are unordered in both the sender and first-load snapshots. Matching uses
`row_key` and `row_hash`, not row position; the query avoids a global sort to keep
large exports from exhausting BigQuery memory. Message contents are unchanged.
GCP setup ([`pubsub/scripts/setup.sh`](../../../pubsub/scripts/setup.sh)),
deploy/test steps and the message format are owned by
[setup-pubsub-export.md](../../how-to/setup-pubsub-export.md).
Exports are configured in `databuffet-nonprd` only. The inventory is listed below;
deployment status is owned by that guide.

**Run status comes from the Dataform API, not from Dataform actions** (redesigned
2026-10-25). There are no start/end actions and no per-run log table. The publisher
discovers scheduled and manual runs with `workflowInvocations.list`. Each
[`WorkflowInvocation`](https://docs.cloud.google.com/dataform/reference/rest/v1/projects.locations.repositories.workflowInvocations)
provides `workflowConfig` (a resource name ending in `workflowConfigs/<scheduler>`;
unset = manual), `state`, and `invocationTiming.startTime` / `endTime`. The publisher lists
with `filter=invocation_timing.end_time > "<checkpoint>"` and a `fields` mask, and follows
`nextPageToken` (pages can be empty while a token remains); `orderBy` on the timing fields
is rejected by the API.
Selected tags are in
[`invocationConfig.includedTags`](https://docs.cloud.google.com/dataform/reference/rest/v1/InvocationConfig)
when present; target-selected and whole-workflow runs need not have tags. Use
[`workflowInvocations.query`](https://docs.cloud.google.com/dataform/reference/rest/v1/projects.locations.repositories.workflowInvocations/query)
to check actual action targets and their states — always with the `fields` mask
`workflowInvocationActions(target/name,state),nextPageToken`: the full response of a
`daily_process` run is ~2 MB (every action's SQL).
Adding a scheduler or running by hand needs no change in Dataform or in the Dataform UI.

Bookkeeping tables live in `process_dataset`; every view read by Pub/Sub lives in its
own dataset `pub_sub` (`databuffet.PUB_SUB`, file under `definitions/view/pub_sub/`).
Every action carries tag `pub_sub` (`databuffet.TAG_PUB_SUB`), which **no scheduler
runs** — see "Deploy" below:

| File | Builds | What |
|---|---|---|
| `mart_export_config.sqlx` | `process_dataset.mart_export_config` | One row per exported table. `CREATE TABLE IF NOT EXISTS`, then syncs from `includes/controller/mart-export-config.json` (inserts new tables, refreshes `task_group` and `send_order`, and removes entries no longer configured after claims/recovery are clear). Schema in its OKF card (linked below) |
| `mart_sent_state.sqlx` | `process_dataset.mart_sent_state` | One row per data row sent. `CREATE TABLE IF NOT EXISTS`, cluster `table_name, row_key`. Schema and writers in its OKF card (linked below) |
| `pub_sub/pub_sub_schema.sqlx` | dataset `pub_sub` (tags `view` + `pub_sub`) | `CREATE SCHEMA IF NOT EXISTS ... OPTIONS(location=REGION)`, the same bootstrap as `validated_schema_*` / `cdc_schema`. `definitions/pub_sub/` is the layer folder for future shaping tables before Pub/Sub |
| `view/pub_sub/export_<table>.sqlx` × 9 | `pub_sub.export_<table>` (views, tags `view` + `pub_sub`) | TA app org tables for the AI team (below): the columns of the org sample sent 2026-11-02, `row_key`, `row_hash` |
| `view/pub_sub/export_<table>.sqlx` × 36 | `pub_sub.export_<table>` (views, tags `view` + `pub_sub`) | AI team sample tables (below): schemas and keys in the [OKF export index](../../okf/view/pub_sub/index.md) |
| `view/pub_sub/export_<set>.sqlx` × 12 | `pub_sub.export_<set>` (views, tags `view` + `pub_sub`) | Commission sets for TF (below): the columns of the sample sent to TF on 2026-10-14, `row_key`, `row_hash` |

**Commission sets for the TF team** (company ag01; added 2026-11-02).
`table_name` = the message `table`; topic `export-commission-<set>`; all have
`trigger_scheduler = daily_process`. Columns, names, order and JSON types follow the sample
`commission_tf_ag01_2026` sent to TF on 2026-10-14 (e.g. `company_source_id`), not the source
column names. Folder date = the column the first-load files are split by (`snapshot_date`;
master data has none and goes under the export date).

The six document exports (`order`, `invoice`, `credit_note`, `debit_note`, `receipt`,
`chqri`) cover all years, including historical and future dates, for `ag01` only.
The sample year does not restrict export coverage. All other filters remain in place;
the SQL headers list each deviation from the original SQL Server queries.

| Set (`table`) | View | Natural key (`primary_key`) | Built from (validated_mac5 unless noted) | Folder date |
|---|---|---|---|---|
| `order` | `export_order` | `company_source_id`, `Order_Type`, `Order_No`, `No` (`No` NULL on a document without lines) | `mih`, latest `mie` row per document, `mil`, `stk`; all document types, not cancelled | `Order_Date` |
| `invoice` | `export_invoice` | `company_source_id`, `Invoice_No`, `No` | `mih` (IS), `mie`, `mil`, `stk` | `Invoice_Date` |
| `credit_note` | `export_credit_note` | `company_source_id`, `CN_id`, `no` | `mih` (BS), `mil`, `stk`, `ar_s` | `CN_Date` |
| `debit_note` | `export_debit_note` | `company_source_id`, `DN_id`, `no` | `mih` (AS), `mil`, `stk`, `ar_s` | `DN_Date` |
| `receipt` | `export_receipt` | `company_source_id`, `mirvnos`, `mirlistno`, `cqlno`, `cqlbank`, `cqlautono`, `chqbank`, `chqdatec`, `chqtag` (cheque columns NULL for cash) | `mir` (RS), `mih`, `cql`, `chq`, `ar_s` | `Payment_Date` |
| `chqri` | `export_chqri` | `company_source_id`, `chqno`, `chqbank`, `chqdatec`, `chqtag`, `cqlvnos`, `cqlbank`, `cqlautono`, `cqlsys` | `chq` (type 1), `cql` (RS) | `cqldate` |
| `status` | `export_status` | `company_source_id`, `id` | `ar_s` | export date |
| `company` | `export_company` | `company_source_id`, `id` (customer code) | `deb` | export date |
| `sell` | `export_sell` | `company_source_id`, `id` | `per` (hidden sellers included) | export date |
| `warehouse` | `export_warehouse` | `company_source_id`, `id` | `sto` | export date |
| `stk` | `export_stk` | `company_source_id`, `stkcode` | `stk` | export date |
| `company_source` | `export_company_source` | `company_source_id` | `dimension_table.dim_company` (ag01) | export date |

**TA app org tables for the AI team** (added 2026-11-02; org data reaches the AI team through
Pub/Sub only). One view and topic per TA app table, `table_name` = the app table, topic
`export-ta-<table>`, `trigger_scheduler = daily_process`. Columns follow the org sample
(one file per app table): no app-generated `id` / `created_at` / `updated_at`, `company_id` = company
code, ranges `[valid_from, valid_to)` where org center's inclusive end day becomes `valid_to + 1 day` for
units and seats (memberships too) and 2066-12-31 becomes NULL. Sources are `org_center`
tables plus the MDS mapping used by `export_employees`; a unit/seat change is exported after
the next successful `daily_process` run.

| Set (`table`) | View | Natural key (`primary_key`) | Built from |
|---|---|---|---|
| `org_levels` | `export_org_levels` | `company_id`, `depth` | `org_center_unit` (depth 1-3; no team level) |
| `org_units` | `export_org_units` | `company_id`, `id` (`unit_id` repeats across companies) | `org_center_unit` minus COMPANY rows; extra column `region_code` (PS1 on PS1-1..PS1-5) |
| `positions` | `export_positions` | `company_id`, `code` | `org_center_member` |
| `employees` | `export_employees` | `person_key` | `org_center_person` + people of `org_center_exception` without a seat, named from `mds_data_org_employee_mapping_center` |
| `memberships` | `export_memberships` | `company_id`, `employee_id` | `org_center_member` folded per person and company; status from today's seats |
| `appointments` | `export_appointments` | `company_id`, `membership_id`, `org_unit_id`, `position_id`, `valid_from` | `org_center_member`; extra column `zone` (TA DepartmentID) |
| `member_links` | `export_member_links` | [Key contract](../../okf/view/pub_sub/export_member_links.md#grain-and-key) | `org_center_link` |
| `access_exceptions` | `export_access_exceptions` | `source_row_id` + every scope column | `org_center_exception`, arrays split |
| `customer_ta_assignments` | `export_customer_ta_assignments` | [Key contract](../../okf/view/pub_sub/export_customer_ta_assignments.md#grain-and-key) | `org_center_customer_ta`; [membership company contract](../../okf/view/pub_sub/export_customer_ta_assignments.md#schema) |

### AI team sample tables

One export view per AI team sample table: the 31 tables of the 2026-10-26 package,
`rls_ta_customer` (rls sample), `mds_data_ta_dashboard_display_control` (dashboard display control),
and the three D-ERP price dimensions `dim_price`, `dim_price_tier` and `dim_price_channel`.
`table_name` = the BigQuery table name in
lower case; view-based topics omit the leading `view_` from that name. Topic routing and triggers are owned by
[`mart-export-config.json`](../../../includes/controller/mart-export-config.json). Except for the company export linked below, columns, names and order follow the
sample CSV header, read from the same source for the whole table (the sample filters are not applied), so they
keep the SK columns of the sample. Dimension SKs remain stable for matching natural keys; current fact row-key
rules and migration scope are owned by the
[coding standard](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). Where a table has no unique business key the key is the business
columns plus `occurrence` (position of the row among rows with the same key, ordered by their data JSON).
The company export schema is owned by its [OKF card](../../okf/view/pub_sub/export_view_dim_company.md#schema).

Price mapping, including the ambiguous and unmatched cases, is owned by the
[dim_price card](../../okf/dimension/dim_price.md); the
[quantity lookup example](../../okf/dimension/dim_price_tier.md#examples) shows the product and tier joins.
The [OKF export index](../../okf/view/pub_sub/index.md) links to each view's authoritative
schema, source and key. Deployment is deferred until the AI team has tested
the samples; the stopping point and future activation procedure are owned by
[setup guide, section E](../../how-to/setup-pubsub-export.md#ส่วน-e--ตารางตัวอย่างของทีม-ai-36-ตาราง).

Measured 2026-11-02 against the limits of the Cloud Workflows publisher the Cloud Run jobs replace (about
41,000 rows per execution shared by every table; first loads go through GCS files): daily changed rows (NEW + UPDATE + DELETE, two
consecutive nights, time travel of the base tables) are a few hundred or fewer for the dims and `rls`/`mds` tables,
about 20,000 for `view_fact_transcation`, 13,000-29,000 for `dim_pump_information`, about 53,000 for
`view_dim_aging_history` (a new as-at snapshot of about 27,000 rows each night and the previous day's snapshot
deleted), and 0.7-2.7 million for `fact_order`, `fact_delivery` and `fact_transaction_delivery` (their SKs were
`ROW_NUMBER()` over the whole table at measurement time); `fact_quotation` shifted the same way (67 of 1,624 sample rows still match
8 days later). Row counts and key uniqueness were checked on the compiled views; each sample is contained in its view on the
sample columns except where an SK was regenerated since the sample was cut.

The send job is sized for these volumes: about 7.9 million messages in a normal night (the fact tables
and `dim_pump_information`), up to about 20 million in the worst night (when the SKs of
`dim_target_product_group_by_sale_dayofwork`, 12.7 million rows, all move). A night that does not
finish within the time limit of one send run is finished by the following check runs (see "Send job").
Deploying the 45 export views still held back follows the cutover to the Cloud Run publisher.

The authoritative table schemas and writer contracts are in the OKF cards for
[`mart_export_config`](../../okf/process/mart_export_config.md#schema) and
[`mart_sent_state`](../../okf/process/mart_sent_state.md#schema). The publisher reads config
columns by name.

The `MERGE` inserts new export tables and refreshes `task_group` and the 1-based `send_order`
from the JSON position for every configured table. It preserves the other columns of an existing
row, including `source_view`, `topic`, `trigger_scheduler`, `last_invocation_id`,
`last_invocation_end`, `claimed_at` and `seeded_at`. Rows removed from the JSON are deleted only
when their `claimed_at`, `group_claimed_at` and `recovery_*` fields are clear; otherwise the
action fails so publishing or recovery can finish first. `task_group` is required for every JSON entry:
Dataform compilation fails when one has none.

**A new export table starts unseeded.** The config MERGE sets
`last_invocation_id`, `last_invocation_end`, `claimed_at` and `seeded_at` to NULL.
`seeded_at` is the durable initialization marker, independent of expiring claims.
Table creation and backfill behavior are described in the
[config reference](../../okf/process/mart_export_config.md#how-it-is-built).
Tag `pub_sub`, setup, merge and deployment never seed sent state or write first-load files.
The publisher returns `not seeded: waiting for the first-load export` before any Dataform
or BigQuery call for an unseeded table; it cannot advance, claim or publish that table.
The first-load execution, transaction, claim cleanup and retry procedure are owned by
[onboarding guide B3](../../how-to/setup-pubsub-export.md#3-โหลดครั้งแรกด้วยไฟล์-ครั้งแรกที่ทีมต่อ-topic-นั้นเท่านั้น);
the TF rollout date and sequence are in [section C](../../how-to/setup-pubsub-export.md#ส่วน-c--ชุด-commission-ของทีม-tf).

Before the MERGE, the transaction that removes retired config rows also runs a repeatable
migration that renames the 12 AI view routes still
using their original `export-ta-view_*` topics. Only `topic` changes in that route migration; checkpoints, claims,
recovery fields and sent state are preserved, while the MERGE refreshes `task_group` and
`send_order`. TF commission routes are untouched when present in the JSON.
Follow the [deployment migration procedure](../../how-to/setup-pubsub-export.md#a11-ย้าย-config-ของ-ai-routes-ก่อน-rebuild-publisher)
before rebuilding the publisher. Other changes to an existing export table's
view/topic remain deliberate manual changes. Export-view name resolution
and validation are described in the [config reference](../../okf/process/mart_export_config.md#how-it-is-built).

**Check job** (every 5 minutes, `main.py check`, 1 vCPU / 512 MiB, one task, service account
`datamart-publish-checker`). It reads `mart_export_config` by column name, then for each row
(skipping a row whose seeded_at is NULL before any Dataform or BigQuery call):

1. List the invocations that ended after `last_invocation_end` (the last 48 hours while it
   is `NULL`), excluding `last_invocation_id`. None → nothing for this table. The newest
   `SUCCEEDED` invocation that triggers the table is the export
   invocation: with `trigger_scheduler` set, one whose `workflowConfig` is that
   configuration (no actions query; manual runs never trigger); without it, one whose
   action `table_name` is `SUCCEEDED` (its actions are queried). None of them qualifies
   (failed, or did not trigger the table) → only advance `last_invocation_*` to the newest
   ended invocation, guarded like the claim below.
2. A table with an export invocation and no live claim is to be sent. When at least one is,
   the check job starts the send job - never while an execution of it is still running.
   A failure posts to Slack (webhook in Secret Manager secret `slack-datamart-dataform`).

**Send job** (`main.py send`, 5 tasks in parallel, 2 vCPU / 4 GiB each, task timeout 30 minutes,
no task retries, service account `datamart-publisher`). It reads `task_group` and `send_order` from
`mart_export_config`. Tables are grouped by `task_group`; groups are ordered by the minimum
`send_order` of their members, and tables within a group use `send_order`. Dataform sets this value
to the table's 1-based position in `mart-export-config.json`, with
the five large ones (`fact_order`, `fact_transaction_delivery`, `fact_delivery`, `fact_quotation`,
`target`) at the top. Every task takes the next group, in that order, that has at least one seeded
table (a group whose tables are all unseeded is never claimed) and works through its tables
one after another, then takes the next group, until none is left. The task atomically sets
`group_claimed_at` on every row in the group only if no
member has a live group or table claim; competing tasks skip that group. It releases the group
after processing its members, and a crashed task's group claim expires after 35 minutes.
Every DML on `mart_export_config` (and the `mart_sent_state` MERGE) is retried a bounded number of
times with a short random backoff when BigQuery aborts it for a concurrent update. A group release
that still fails is logged as a warning and does not fail the task; the claim expires by itself.
Before claiming any group, the send job requires a nonempty config with unique, nonblank
`table_name` values, nonblank `task_group` values, and unique positive integer `send_order`
values. Invalid scheduling config fails the task. Per table:

1. Resolve the export invocation exactly as the check job does.
2. Claim the row atomically: `UPDATE mart_export_config SET claimed_at = <now>
   WHERE table_name = ... AND (claimed_at IS NULL OR claimed_at < now - 35 minutes)
   AND (last_invocation_end IS NULL OR last_invocation_end < <end_time>)`. 0 rows
   updated → another task or the first-load script holds it, or this or a newer invocation
   was already handled → skip. (The first-load script keeps its own 30-minute assertion, shorter
   than the claim, so it never exports a table the publisher may already have taken over.)
3. **Recovery** - only when the row's claim was expired rather than empty, i.e. the previous
   run on this table died. What Pub/Sub accepted is what the **record subscription**
   wrote (storage and subscription setup: [setup guide, A3](../../how-to/setup-pubsub-export.md#a3-รัน-setupsh)).
   The task waits until the backlog of that subscription is 0, takes the messages
   published since the dead claim started, de-duplicates them by `message_id` (the record is
   at-least-once), keeps the newest message per `row_key` and MERGEs `row_key` / the
   fingerprint of the message `data` text (NULL for DELETE) into `mart_sent_state`. If the
   recovery fails, the durable `recovery_started_at` retains the earliest unresolved dead
   claim across subsequent reclaims. `recovery_until` retains the latest dead claim plus the
   30-minute task limit. Recovery requires two distinct zero-backlog samples newer than that
   bound and at most two minutes old; missing or stale metrics fail closed. Both recovery
   fields are cleared only after the recovered state has been merged. Recovery checks the record
   table's actual partition retention first, including the two-minute lookback and UTC day
   boundary, and reads the record subscription's actual message retention (default seven days).
   The sender has `roles/pubsub.viewer` on each record subscription for this metadata read.
   An interval expired in either storage layer, or expiring before this task finishes, fails
   closed without clearing recovery or publishing a new diff.
4. Diff the export view with `mart_sent_state` (`pubsub/sql/diff.sql`, one query, reading only
   `row_key`, `row_hash` `WHERE table_name = ...`) into a staging table
   `pubsub_staging.stg_<table>` (tables expire after 1 day): absent key = `NEW`,
   different hash = `UPDATE`, key only in state = `DELETE`; equal hash = not sent. The same
   query builds each message (`primary_key` = `row_key` text, `data` = `TO_JSON_STRING` of the
   data columns, `null` for `DELETE`; no attributes; `run_date` = the date of the diff in
   Asia/Bangkok).
5. Read the staging table with the Storage Read API (views cannot be read that way, hence the
   staging table) and publish batches of 1,000 messages with concurrency. Every 1,000,000 sent rows,
   and at the end, MERGE exactly the rows Pub/Sub accepted into `mart_sent_state`
   (`invocation_id` = the invocation, `sent_at` = now; DELETE removes the key).
6. Set `last_invocation_id`, `last_invocation_end` and `claimed_at = NULL`, only while
   `claimed_at` still holds this run's claim (lost claim → failure).

**Time limit.** A task stops by itself at 25 minutes: no new batch starts, the rows already
sent are recorded, the claim is released, Slack is told - and `last_invocation_*` is **not**
moved. Query, load, Storage Read, HTTP and publish-backpressure waits use the remaining
task budget. Publishing drains until minute 26, recording finishes by minute 28, and the
remaining minute is reserved for cleanup and release before the task's minute-29 deadline.
A failed drain or record keeps the table claim for recovery. The next check run (within 5 minutes) sees the same invocation again and the send
job continues with the rest (a new diff). The send task reports accumulated failures once to
Slack, including recovery timeouts, resolve/advance, configuration and group ownership failures.
A failed table leaves the memory and
the claim as they are: the claim expires after 35 minutes and the next run recovers from the
record subscription (step 3).

Several new invocations since the last one are handled as one: the diff compares the
current view, so only the newest matters. Invocation end times carry nanoseconds; the
publisher cuts them to microseconds before they reach a BigQuery `TIMESTAMP`.

**Duplicates.** Publishing and recording sent state are separate operations. A crash between
them is repaired by step 3, which keeps `NEW` messages from being sent twice. What can still
arrive twice is an `UPDATE` (or `DELETE`) of the same row, and a message Pub/Sub itself
redelivers (same `publish_time`); receivers must follow the idempotency and delivery rules in
the [message guide](../../how-to/setup-pubsub-export.md). Exactly-once delivery is not enabled
on team subscriptions: it does not remove duplicates created on the publish side, only
redeliveries after an acknowledgement.

**Order is read from the table at runtime.** The `mart_export_config` Dataform action records the
JSON position in `send_order`; the Cloud Run image does not contain or read the JSON. Adding or
removing an export is a change to `includes/controller/mart-export-config.json` followed by a run
of the `mart_export_config` Dataform action. No image rebuild is needed for config-only changes.
For the existing-table schema upgrade before running this SQLX version, follow
[setup A1](../../how-to/setup-pubsub-export.md#a1-สร้างตาราง-bookkeeping-และ-export-view).
`setup.sh` still reads the JSON to create topics and grant view access; run it when those GCP
resources need to be provisioned.

**Export view contract** (every export view):

- data columns first, under the **source table's column names** (no renaming, no
  `company_source_id`) — except the commission, TA app and AI team sample sets, which keep the names
  agreed in their respective samples. The AI team sample sets retain their sample SK columns,
  including fact row SKs; other exports exclude dimension SKs and incidental daily values
  that make unchanged rows look changed. Date-driven membership status is intentional;
  its transition rules are owned by the
  [`export_memberships` schema](../../okf/view/pub_sub/export_memberships.md#schema);
- no cleaning helpers when the source is a dim/fact: it was cleaned when it was built.
  Round decimals to a fixed scale before they reach the hash if the source does not;
- `row_key = TO_JSON_STRING(STRUCT(<key columns>))` becomes `primary_key`, unique and
  never NULL. Each view's OKF card owns its key definition; this may use an SK or include
  `occurrence` to distinguish repeated business keys in the AI team sample sets;
- `row_hash = FARM_FINGERPRINT(TO_JSON_STRING(<all data columns>))` — the fingerprint of
  exactly the message `data`, so it changes only when something sent changes.

`dim_company`'s key is `CompanyID` alone (5 rows, unique, never NULL). Checked
2026-10-25 with time travel: the row hashes are identical across the snapshots after the
2026-10-22, 10-23, 10-24 and 10-25 runs.

**Add a table to the export:** add an `export_<table>.sqlx` view in
`definitions/view/pub_sub/` (schema `databuffet.PUB_SUB`, tags `TAG_VIEW` +
`TAG_PUB_SUB`, `dependencies` including `pub_sub_schema`) following the contract, then
one entry under `tables` in `mart-export-config.json` (`table_name` = the message
`table`, `source_view`, `topic`, `task_group` = the name of its group (required; an existing group
or a new one), `source_tables` = the base tables the view reads, the first being the table or view
the export view reads and the others one object per upstream dataset it reads through;
`trigger_scheduler` = the Dataform workflow configuration
whose successful run triggers it, or omit it to trigger on the action named `table_name`;
optional `snapshot_date` = `{"column", "format"}` of the document date that splits the
first-load files into date folders), then run tag `pub_sub` to create the view and run the
`mart_export_config` Dataform action to add its row and `send_order`. The row remains unseeded until
its first manual Cloud Shell snapshot seeds state and writes files together. Re-run
`pubsub/scripts/setup.sh`: it creates the topic, dead-letter topic and record subscription, grants
the publisher read on the export view, and configures dataset authorizations as described in the
[setup guide](../../how-to/setup-pubsub-export.md#a3-รัน-setupsh), which owns the authorization scope
and the procedure for exports reading datasets outside it. It also deploys the jobs, but a
config-only change reuses the same image because the config JSON is not part of the image.
Consumer teams get the new topic through
`pubsub/scripts/add-consumer.sh`. To remove a table, remove its JSON entry and run the
`mart_export_config` action after its claims and recovery fields are clear. For existing exports,
follow the config lifecycle and scoped AI-route migration above.

### Deploy

Run by hand, with no workflow configuration change. Once the code reaches `nonprod`,
follow these steps for the first deployment and whenever an export table is added:

For an existing installation, first follow the [migration procedure](../../how-to/setup-pubsub-export.md#a11-ย้าย-config-ของ-ai-routes-ก่อน-rebuild-publisher),
which pauses publishing and completes recovery before running the Dataform actions below.

1. In Dataform → Releases & Scheduling → release config `production`, select
   **New compilation** and wait for success, or verify that its existing live
   compilation's commit SHA includes the change on `nonprod`.
2. Verify the successful result is live and its commit includes the change, then
   run tag `pub_sub` from `production` with **include dependencies off**.

Manual execution uses the release's live compilation result
([Dataform compilation reference](https://docs.cloud.google.com/dataform/docs/configure-compilation#trigger-execution-release-configuration)).
The run creates the `pub_sub` dataset (in `databuffet.REGION`), the export views and
the two tables, and adds missing export config rows (unseeded until their first manual
Cloud Shell snapshot). Re-running follows the config lifecycle described above, including
refreshing `task_group` and `send_order` from the JSON while preserving checkpoints, claims and
sent state for retained rows. The action backfills `seeded_at` from existing sent state as before.
No Dataform workflow configuration carries
`pub_sub`. Do not use tag `view` for this: it deploys every view and skips the two
tables. Then set up GCP and test per
[setup-pubsub-export.md — ส่วน A](../../how-to/setup-pubsub-export.md#ส่วน-a--deploy-และทดสอบ-publisher).

---

## `rls_ta_customer.sqlx` — TA customer access (who sees which customer)

Precomputed customer access for the TA app (via Pub/Sub later) and the AI Advisor.
The authoritative [table contract](../../okf/process/rls_ta_customer.md) owns the schema,
refresh cadence, grant expansion rules and safe mart filtering example. This table
is separate from the Customer360 / Power BI access map described above.

# Dimension Layer — Special Cases

> **LLM context**: Source branches and special behaviors that must remain intact when
> editing a dimension. The common stable-SK sync is described in
> [merge-sk-pattern.md](merge-sk-pattern.md).

## `dim_sale_representative` — stable SK sync over two source branches

The complete source snapshot preserves the two CTE sources UNION ALL'd below. The
natural key includes the validity and order-window dates; matching rows keep their SK, and
new rows receive an SK after the current maximum.

- **`mds_rep`**: reps from `mds_data_sales_representative_master` (full org structure,
  StartDate/EndDate intervals, MdsID populated), built through three CTEs —
  see **CustomerFlag roll-up** below.
- **`ledger_rep`**: per-employees from `ref(databuffet.VALIDATED_MAC5, 'per')` —
  `pernamet` parsed via `REGEXP_EXTRACT` into name/surname/nickname;
  DepartmentID/DepCode/CostChannelID/ProvinceID/flags = NULL;
  sentinel dates `1900-01-01` → `2499-12-31`; `MdsID = NULL`.
The source ordering expression is used only when allocating SKs to new rows; existing SKs
are matched by the natural key.

### Order windows (2026-10-28)

`OrderStartDate` / `OrderEndDate` are DATE fields carried from MDS through
`mds_base`, `mds_rep`, and the final dimension. Ledger rows carry typed DATE NULLs;
the order-window fields remain part of the SaleRepSK natural key. Classification of CustomerFlag-only
rows is defined in the CTE table below; order-window rows stay as standalone rules.

`dim_sale_representative_last` includes both fields in its raw latest-row partition
alongside the existing company / department / employee / rule keys. `agg_normal`
only considers rows without OrderStartDate, with both window fields added to its
company / employee partition. `final` retains window rows even when a normal
fallback exists, so distinct windows and the fallback survive together. Its ledger
snapshot leaves both window fields NULL. `update_sk_sale_rep_group` still backfills
the hierarchy after the snapshot rebuild.

The `_last` snapshot combines current rule rows with current ledger employees from
`validated_mac5.per` before one stable-key MERGE. Matching keys reuse their SKs;
employees absent from `per` are removed from the ledger rows. Ledger rows have NULL
department, hierarchy, rule attributes and validity dates.

The shared bill-matching contract is owned by
[fact-layer.md](../fact/fact-layer.md#sale-rep-order-window-matching-2026-10-28).

### CustomerFlag roll-up (2026-09-15)

Users enter a customer-list rule as its **own mds row** — same companyID / EmployeeID /
DepartmentID as the real rule row, `CustomerFlag` filled (`A|B|C`), and DepCode /
CostChannelID / ProvinceID empty and no OrderStartDate. Those rows must **not** reach
the dim as standalone rows: they have no rule columns, so `dim_sale_representative_last`
would treat them as the employee's "normal" row (its `agg_normal` CTE ignores
CustomerFlag) and collapse the employee's other non-window rules away.
Measured before the fix: both test employees
dropped from 3 rows to 1 in `_last`, moving 371 and 243 fact rows in the `*Last` columns.

So `mds_rep` is now built in three steps:

| CTE | What it holds |
|---|---|
| `mds_base` | the old `mds_rep` body — cleaned mds rows, `is_active = TRUE` |
| `flag_only` | rows with CustomerFlag and no DepCode / CostChannelID / ProvinceID / OrderStartDate |
| `rule_rows` | everything else (the real rules) |
| `mds_rep` | `rule_rows` + CustomerFlag pulled in from `flag_only` |

The pull-in is a **correlated scalar subquery** (`STRING_AGG` over `flag_only`) so several
flag rows can feed one rule row without fanning out, combined with any inline
CustomerFlag through `ARRAY_TO_STRING([...], '|')`. It attaches only to rows where
`DepCode IS NOT NULL`, matching on companyID + EmployeeID + DepartmentID with
**overlapping** date ranges (`r.StartDate <= f.EndDate AND f.StartDate <= r.EndDate`).

A flag row with no rule row to attach to **disappears silently** — see
`document/operations/known-issues.md`. Column order in `mds_rep` is written out
explicitly because `combined` UNION ALLs it with `ledger_rep` positionally.

Verified 2026-09-15: with 0 flag-only rows in mds, new and current output are identical
(2,349 rows, `EXCEPT DISTINCT` = 0 both directions).

## `dim_stk_mkt` — 'Waiting Master' placeholders

The complete source preserves CTE `mds_mkt` (active MDS rows) UNION ALL CTE `waiting_master` —
every distinct `stkcode` from `ref(databuffet.VALIDATED_MAC5, "stk")` that
`NOT EXISTS` in `mds_mkt` (matched on StkCode + companyID), with
`MarketingGroupID='999'`, `SubMarketingID='9999'`, `SegmentID='99999'`, names
`'Waiting Master'`, `MdsID = NULL`. The daily rebuild numbers both branches together; see the [table card](../../okf/dimension/dim_stk_mkt.md#grain-and-key).

## `dim_doctype` / `dim_holiday` — no surrogate key

Full-rebuild files (since 2026-07-20) that intentionally have **no SK column**:
plain SELECT of natural columns + MdsID, `WHERE is_active = TRUE`, no ROW_NUMBER,
no uniqueKey. (Historically their SK machinery was commented out and they
MERGEd on natural keys.) `dim_holiday` has `dependencies: []`.
Both keep `bigquery.clusterBy` matching the pre-existing BigQuery tables
(`HolidayDate, LongWeekEndFlag` / `AccountCategory, Code`) — required because
`CREATE OR REPLACE TABLE` cannot change an existing table's clustering spec
(first-night failure 2026-07-21, fixed by adding the clusterBy back).

## `dim_rate_target` — MDT percent reallocation

The stable-key sync keeps the source rows and dependencies. The same action then recomputes
`Percent` for departments under director 'MDT' using `mdt_base_data` (rows joined to
`dim_department_last` and `dim_director_last`, filtered to `DirectorName = 'MDT'`),
head-count per month, and the existing updates for per-month rows and NULL-month rows.
Its `dependencies` include `dim_department_last`, `dim_director_last`, and
`update_sk_sale_rep_group` because `dim_department_last.DirectorSK` is filled by that
step before the MDT calculation.

## `dim_customer_report_info` — mds + every invoice name (2026-10-01)

**Stable SK since 2026-10-28**: `type: "operations"` MERGE ON `CompanyID` + `CustomerReportKey`
(new stored column = name with all whitespace removed). Existing names keep their
`CustomerReportInfoSK` and get every other column updated; new names get `max_sk + ROW_NUMBER()`
ordered by `CompanyID, CustomerReportKey`; names gone from the source are kept (no delete); the
`-1` row is inserted only if missing. The target must pre-exist — **never rebuild it from scratch**
(a rebuild would renumber SKs). See [inventory (b2)](inventory.md#group-b2--mds--invoice-merge-1).

Sources, deduplication, output columns, hierarchy dependencies, segment rules, TA rules
and Power BI relationships are owned by the
[Customer Report Info section](../view/view-layer.md#customer-report-info--customer-segment-2026-10-01).
For its view-backed build dependencies, follow [view-layer.md](../view/view-layer.md) § Run order.

## `dim_change_district` — mds-sourced but not a MERGE

`type: "table"` — plain full-rebuild SELECT from `mds_data_change_section_master`
joined to dim_company, filtered `WHERE t1.is_active = true`. No SK, no BEGIN, no
tombstone needed (inactive rows drop out on every rebuild).

## `dim_product_series` — active series master

The source is `mds_data_product_series_master`; `SeriesCode` is the natural key. The stable
key sync retains the source rows, and `dim_target_series_mdt` maps unknown series codes to
`OTHERS`.

## `dim_target_product_group_by_sale` / `_dayofwork` — target snapshots

`dim_target_product_group_by_sale` synchronizes its complete source snapshot on the
established natural key and retains matching SKs. Both dimensions keep their existing
source calculations and joins.

`dim_target_product_group_by_sale_dayofwork` is held: it retains its original daily
full rebuild and regenerates `TargetBySaleDayofworkSK` with `ROW_NUMBER()`. Consumers
must not persist that key across runs. It joins `dim_calendar` to expand targets over
working days and joins `dim_sale_representative` by natural keys (employee, department,
company, and date range).

## `update_sk_sale_rep_group` — imperative UPDATE step

Not a dim. Builds `temp_data` and runs several `UPDATE <dim>_last SET <FK>SK = ...`
statements to backfill the NULL SK FK columns the `_last` tables declare, then drops
the temp. Must run **after** all `_last` rebuilds (it depends on all 7).

## `dim_calendar` — yearly date spine

Only file tagged `dimension_yearly`. `GENERATE_DATE_ARRAY` spine + dim_holiday join +
weekend/holiday/long-weekend flags via window functions; TEMP → DELETE matching dates
→ INSERT (idempotent).

## `dim_aging` — the monster

~500 lines; AR aging engine over many validated/curated MAC5 tables, a history table
(`dim_aging_history`), a view (`view_dim_aging`), `fact_mir_vs` (repo-managed since
2026-07-20 and declared in `dependencies[]` — see
[fact/fact-layer.md](../fact/fact-layer.md)), and `onetime.cfsinvclose2024`.
The original AR rebuild and history writer remain unchanged; see the
[aging card](../../okf/dimension/dim_aging.md#how-it-is-built) and
[history card](../../okf/dimension/dim_aging_history.md#how-it-is-built) for their contracts.
Read the whole action before editing: it is not template-shaped.

# Dimension Layer — Special Cases

> **LLM context**: Deviations from the canonical MERGE pattern. Check this page before
> editing any of these files with a bulk/mechanical change.

## `dim_sale_representative` — UNION of two sources (rebuilt daily since 2026-07-20)

Full-rebuild file with two CTE sources UNION ALL'd, single `ROW_NUMBER()` over the union:

- **`mds_rep`**: reps from `mds_data_sales_representative_master` (full org structure,
  StartDate/EndDate intervals, MdsID populated), built through three CTEs —
  see **CustomerFlag roll-up** below.
- **`ledger_rep`**: per-employees from `ref(databuffet.VALIDATED_MAC5, 'per')` —
  `pernamet` parsed via `REGEXP_EXTRACT` into name/surname/nickname;
  DepartmentID/DepCode/CostChannelID/ProvinceID/flags = NULL;
  sentinel dates `1900-01-01` → `2499-12-31`; `MdsID = NULL`.
SK ordering puts mds rows first (`CASE WHEN MdsID IS NULL THEN 1 ELSE 0 END`).

### Order windows (2026-10-28)

`OrderStartDate` / `OrderEndDate` are DATE fields carried from MDS through
`mds_base`, `mds_rep`, and the final dimension. Ledger rows carry typed DATE NULLs;
the existing SaleRepSK ordering is unchanged. Classification of CustomerFlag-only
rows is defined in the CTE table below; order-window rows stay as standalone rules.

`dim_sale_representative_last` includes both fields in its raw latest-row partition
alongside the existing company / department / employee / rule keys. `agg_normal`
only considers rows without OrderStartDate, with both window fields added to its
company / employee partition. `final` retains window rows even when a normal
fallback exists, so distinct windows and the fallback survive together. Its ledger
INSERT leaves both window fields NULL. `update_sk_sale_rep_group` still backfills
the hierarchy after the snapshot rebuild.

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

## `dim_stk_mkt` — 'Waiting Master' placeholders (rebuilt daily since 2026-07-20)

Full-rebuild file: CTE `mds_mkt` (active mds rows) UNION ALL CTE `waiting_master` —
every distinct `stkcode` from `ref(databuffet.VALIDATED_MAC5, "stk")` that
`NOT EXISTS` in `mds_mkt` (matched on StkCode + companyID), with
`MarketingGroupID='999'`, `SubMarketingID='9999'`, `SegmentID='99999'`, names
`'Waiting Master'`, `MdsID = NULL`. Single `ROW_NUMBER()` over the union.

## `dim_doctype` / `dim_holiday` — no surrogate key

Full-rebuild files (since 2026-07-20) that intentionally have **no SK column**:
plain SELECT of natural columns + MdsID, `WHERE is_active = TRUE`, no ROW_NUMBER,
no uniqueKey. (Historically their SK machinery was commented out and they
MERGEd on natural keys.) `dim_holiday` has `dependencies: []`.
Both keep `bigquery.clusterBy` matching the pre-existing BigQuery tables
(`HolidayDate, LongWeekEndFlag` / `AccountCategory, Code`) — required because
`CREATE OR REPLACE TABLE` cannot change an existing table's clustering spec
(first-night failure 2026-07-21, fixed by adding the clusterBy back).

## `dim_rate_target` — MDT percent reallocation in post_operations (activated 2026-07-20)

The only full-rebuild mds dim with a real `post_operations { BEGIN ... END }` block:
after the daily rebuild it recomputes `Percent` for departments under director
'MDT' — temp `mdt_base_data` (rows joined to `dim_department_last` →
`dim_director_last`, filter `DirectorName = 'MDT'`), head-count per month
(`COUNT(DISTINCT employee-dept) / 6` + share of NULL-month rows), then two UPDATEs
on `${self()}` (per-month rows, and NULL-month rows using the max total).
This is why its `dependencies` include `dim_department_last`, `dim_director_last`
**and `update_sk_sale_rep_group`** — `dim_department_last.DirectorSK` is created as
NULL and backfilled by `update_sk_sale_rep_group`, so the post_op must run after
that backfill or the MDT join matches nothing.

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

## `dim_product_series` — hard-coded rows (pending move to mds)

`type: "table"`, added 2026-10-02 (`e57d635`). It does **not** read `mds_dataset`: the
rows are typed into the file with `UNNEST([...])` from BI's `dim_product_series.xlsx`
(`100001` TITAN, `999999` OTHERS). `SeriesSK = ROW_NUMBER() OVER(ORDER BY SeriesCode)`,
so it regenerates daily like the full-rebuild dims. There is no `-1` row:
`dim_target_series_mdt` maps unknown series codes to `OTHERS` instead.

Pending: move it to `mds_dataset` once BI loads the series master there (the file's
own comment). Until then a new series means editing the `.sqlx` by hand. Tracked in
[known-issues](../../operations/known-issues.md).

## `dim_target_product_group_by_sale` / `_dayofwork` — daily full rebuilds

`type: "table"` with `uniqueKey`/`clusterBy` on their SK. `_dayofwork` joins
`dim_calendar` to expand targets over working days and joins
`dim_sale_representative` by **natural keys** (employeeid/DepartmentID/CompanySK/date
range) — so it self-heals the day after any upstream dim change/delete. SKs in these
two tables are ROW_NUMBER-based and **not stable across runs**; do not persist them
outside same-day joins.

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
Read it fully before touching; it is not template-shaped.

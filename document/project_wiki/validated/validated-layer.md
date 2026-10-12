# Validated Layer — `definitions/validated/`

> **LLM context**: 143 files (mac5 87 · cis360 25 · mastersku 12 · saleout_mdt 11 ·
> allkons_commission 8; each source has 1 `validated_schema_*` bootstrap). Pure mechanical
> cleaning: read raw, trim/cast every column with `functionData` helpers, standardize
> `asatdate`, dedup on PK, write to `validated_<source>`. No business logic (rare
> exceptions in mac5).
> **There is NO `primary-keys.json`** — keys are hardcoded per file (see below).
> **3 files add a document-grain purge** (`mih`, `mil`, `mir`): same `type`/`uniqueKey` as
> everyone else, but `pre_operations` builds a TEMP table of today's batch and DELETEs the
> whole document from the target before the body MERGEs that TEMP table in.

## Canonical incremental file (four parts)

```sqlx
config {
    type: "incremental",
    schema: databuffet.VALIDATED_CIS360,
    dependencies: ["validated_schema_cis360", "create_all_table_raw_cis360"],
    tags: [databuffet.TAG_VALIDATED, databuffet.TAG_VALIDATED_INCREMENTAL],
    uniqueKey: ["id"],
    bigquery: { partitionBy: "asatdate", clusterBy: ["id"] },
}

js {
    const sourceTable = { database: databuffet.DATABASE, schema: databuffet.RAW_CIS360, name: name() };
    const sourceTableRef = `${sourceTable.database}.${sourceTable.schema}.${sourceTable.name}`;
    const pk_key = ["id"]        // <-- PK defined HERE (and in uniqueKey above)
    let partition_statement, post_operations_statement;
    if (pk_key && pk_key.length > 0) {
        partition_statement = `QUALIFY ROW_NUMBER() OVER(PARTITION BY ${pk_key} ORDER BY asatdate DESC) = 1`;
        post_operations_statement = `...retry-loop ALTER TABLE ADD PRIMARY KEY NOT ENFORCED...`;
    } else { partition_statement = ""; post_operations_statement = ""; }
}

SELECT
    ${databuffet.functionData.cleanString('id')} as id,
    ${databuffet.functionData.castBool('active_status')} as active_status,
    ${databuffet.functionData.parseFlexibleDatetime('create_date')} as create_date,
    ${databuffet.functionData.parseAsatDate()} AS asatdate,
FROM `${sourceTableRef}`
${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY))`) }
${partition_statement}

pre_operations {}
post_operations { ${ when(!incremental(), post_operations_statement) } }
```

Key mechanics:

- **Incremental window filters on the raw STRING `ASATDATE`** compared to a formatted
  string (1-day look-back, Bangkok time) — not on the parsed DATE column.
- **PK is defined twice**: `uniqueKey` in config (drives Dataform incremental MERGE)
  and `pk_key` in js (drives QUALIFY dedup + NOT ENFORCED PK). Keep them in sync.
- **Empty `pk_key = []`** → no dedup, no PK constraint (append-style tables like `grp`).
- **PK post-op** runs only on full builds (`when(!incremental())`): a
  `WHILE retry_count < 10` loop doing `ALTER TABLE ... DROP PRIMARY KEY IF EXISTS` +
  `ADD PRIMARY KEY (...) NOT ENFORCED` inside `BEGIN...EXCEPTION` (metadata-contention guard).
- Dedup order is usually `asatdate DESC`; some tables order by business columns
  (`mir`: `mirbinvdate DESC`; `grp`: `grpname DESC`).

Reference files:
- Single-source incremental: `definitions/validated/cis360/customer_profile.sqlx`
- Multi-company incremental: `definitions/validated/mac5/mie.sqlx`
- Full-load: `definitions/validated/mac5/grp.sqlx`

> `mih`, `mil` and `mir` keep this config but add a TEMP table + document DELETE in
> `pre_operations` — see
> [Document-grain purge via TEMP table](#document-grain-purge-via-temp-table-mih-mil-mir--2026-09-10).

## Full-load pattern (`TAG_VALIDATED_FULL`)

Differences from incremental: `type: "table"` (full rebuild each run), tag
`validated_full`, usually no `partitionBy`, no incremental WHERE. Everything else
identical. Since `incremental()` is always false for `type: "table"`, the PK post-op
runs **every** run.

- Used **only in mac5** (73 of 86 non-schema files) — all master/reference codes and
  the `tmp_*`, `tbook_*`, `tdis_*`, `match_*`, `pro_*` families.
- Exceptions to note: `mir.sqlx` is `type: "incremental"` but tagged FULL (operator
  grouping); `mih_billing`/`mil_billing` are full-rebuild snapshots.

## Document-grain purge via TEMP table (`mih`, `mil`, `mir` — 2026-09-10)

**Config is unchanged** — still `type: "incremental"` with the same `uniqueKey`. What
changes is that `pre_operations` materialises today's batch once and deletes the whole
document from the target before the body runs:

```sqlx
SELECT * FROM new_data_mil        -- the body just reads the TEMP table

pre_operations {
  CREATE OR REPLACE TEMP TABLE new_data_mil AS
  <the full multi-company SELECT: helpers, incremental window, QUALIFY dedup>
  ;

  ${ when(incremental(), delete_statement) }
}
```

Order of execution: TEMP table → `DELETE` the documents it contains → the body's MERGE
on `uniqueKey`. Because the old rows of those documents are already gone, every row
falls into the MERGE's INSERT branch — so the net effect is delete + insert while the
declared PK still guards against duplicates.

`delete_statement` is built in the js block from two constants:

| Constant | Purpose |
|---|---|
| `doc_key` | document identity — `company_id` + `<t>type` + `<t>vnos` (**no** `listno`) |
| `temp_table` | `new_data_<table>` — the batch, so the doc keys are the already-cleaned values |

```sqlx
DELETE FROM ${self()} AS t
WHERE EXISTS (
  SELECT 1
  FROM new_data_mil AS b
  WHERE b.company_id = t.company_id
    AND IFNULL(b.miltype, '') = IFNULL(t.miltype, '')
    AND IFNULL(b.milvnos, '') = IFNULL(t.milvnos, '')
);
```

**Why the TEMP table** — raw is an external table over GCS AVRO, so reading it twice
(once to collect doc keys, once for the body) doubles the scan for nothing. The TEMP
table reads raw **once** and both the DELETE and the body consume it. It also removes a
whole class of bug: the doc keys are the cleaned values from the batch itself, so they
cannot drift from the `cleanString()` expressions in the SELECT.

**Why the purge at all**: the PK of `mil`/`mir` is line-level (`...listno`), so a MERGE
can only ever upsert — a line deleted at source keeps its old `asatdate` and is then
counted twice. One live example (`ag01/IS/6907004392`) held the same product, quantity
and amount under `millistno` 1 and 2 because the source renumbered the line, doubling
the document to 50,200 THB. Measured on nonprd 2026-09-10:

| Table | rows/doc | stale lines | value double-counted | effect of the change |
|---|---:|---:|---:|---|
| `mil` | 3.12 | 476 | 9.2M THB of `milsum` | purges 473 lines per run |
| `mir` | 3.49 | 506 | 10.4M THB of `mirsum` | purges 504 lines per run |
| `mih` | 1.00 | 0 | — | none — doc key **is** the PK; done for consistency with `mil` |

Verified by simulating the DELETE as a SELECT (2026-09-10): it removes 969,101 rows on
`mil` = 968,628 re-inserted by the batch + 473 purged; `mir` 344,545 = 344,041 + 504;
`mih` 484,891 = 484,891 + 0.

Rules when touching these files:

- Keep the doc key coarser than the PK — that gap (`listno`) is the whole point.
- Mirror the body's row filter inside the TEMP table (`mih`/`mil` filter
  `IFNULL(vnos, '') != ''`; `mir` has none).
- Re-running the same day is idempotent: the DELETE is keyed on the batch, so a second
  run deletes and re-inserts exactly what the first run did.
- `when(incremental())` guards only the DELETE — the TEMP table is created on every run
  because the body always reads it, including on a full refresh.
- The DELETE cannot prune partitions (a document's lines may sit in different `asatdate`
  partitions, which is the problem itself), so it scans the target each run. Cost is
  negligible: the three tables together billed ~3.0 GB/day = ~91 GB/month ≈ $0.57/month
  before the change (real job bytes — **not** `monitor_dataset.dataform_run_action`,
  which double-counts; see `document/operations/known-issues.md` 2026-09-10).

**Deliberately NOT applied to `mie` / `mie_dummy`**: their PK carries
`mieday/miemonth/mieyear/miecus`, so one `(mietype, mievnos)` legitimately holds several
rows. Deleting at `(type, vnos)` grain would drop **67,946 rows across 4,744 documents**
that the batch does not re-supply (measured 2026-09-10) — see
[known-issues.md](../../operations/known-issues.md).

**NULL in a `uniqueKey` column (2026-10-12)**: Dataform's incremental MERGE matches
`uniqueKey` with `=`, so a row whose key column is NULL never matches and is
re-inserted every run. `mie.miecus` (blank customer → `cleanString` → NULL) piled up
98,474 duplicate rows, up to 219 copies each. Fix: key string columns use
`IFNULL(cleanString(...), '')` — the one exception to the empty→NULL rule. `mie_dummy`
has no blank `miecus`. Any other incremental table whose PK includes a column
`cleanString` can null out has the same latent bug.

**Accepted trade-off**: `pre_operations` and the body are statements in the same
Dataform action, but the DELETE lands before the MERGE — if the MERGE fails after the
DELETE, those documents are missing until the next run. The reverse (an INSERT that
never deleted, which would duplicate) cannot happen: Dataform fails the whole action
when `pre_operations` fails.

## Per-source summary

| Aspect | mac5 | cis360 | mastersku | saleout_mdt |
|---|---|---|---|---|
| Raw datasets | `raw_mac5_ag01` + 4 companies | `raw_cis360` | `raw_mastersku` | `raw_saleout_mdt` |
| Default type | mostly `table` (full) | all incremental | all incremental | all incremental |
| Sub-tag | FULL / INCREMENTAL | INCREMENTAL | INCREMENTAL | **none** (only `validated`) |
| PK | table-specific composites | `id` | `prd_id` / `*_id` | wide business composites |
| Partition | `asatdate` when incremental | `asatdate` | `asatdate` | usually none |
| Quirks | multi-company UNION, sign flips, Thai-text cleanup | heavy `castBool` | `prd_*` prefix | vendor subfolders BT/GB/HP/TW, `PARSE_DATE('%Y/%m/%d', ...)` |

### MAC5 multi-company UNION (14 files)

`ap_s, ar_s, cfs, chq, cql, deb, dep, mie, mih, mil, mir, per, stg, stk` UNION ALL the
same table across all 5 company datasets, each block adding a literal `company_id`
as first column (hence `company_id` leads uniqueKey/clusterBy). Extra dependencies:
`create_all_table_raw_mac5_{aa05,ab01,ac02,ak02}`. Only the ag01 block has `moddate`;
others hardcode `CAST(NULL AS DATETIME) AS moddate`.

### MAC5 incremental tables (13)

`mih, mih2, mih_dummy, mil, mil_dummy, mie, mie_dummy, mir, cps, cps_dummy, cql, cst, rcv`
— the transactional invoice/cost/receiving tables.

## Data quality

No Dataform assertions exist anywhere in the project. Quality is implicit:
1. helper casting (`cleanString` → NULL for empties; `SAFE.PARSE_DATETIME` → NULL on bad dates),
2. QUALIFY dedup (one row per PK),
3. NOT ENFORCED PK constraints (optimizer hints),
4. occasional inline filters (e.g. `mih`: `WHERE IFNULL(mihvnos,'') != ''`).

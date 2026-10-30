# Org Center — `org_center_unit` / `org_center_member` / `org_center_person` / `org_center_link`

> **LLM context**: Dataset `org_center` (`databuffet.ORG_CENTER`), folder
> `definitions/org_center/`, added 2026-10-29 for the TA AI Assistant. It is the single
> source of **who sits in which unit and position**; Power BI RLS, the TA app and other
> systems build their own access rules from it later. All four tables are `type: "table"`,
> tag `dimension_daily`, rebuilt every night (`org_center_unit` and `org_center_member` after
> `update_sk_sale_rep_group`; `org_center_person` after `org_center_member`). `org_center_link` (PC → TA) reads
> `mds_dataset.mds_data_pc_ta` and has 0 rows while that MDS table is empty.
> They carry **business codes, not SKs**, so consumers can keep them across days.

## Files

| File | Type | What it does |
|---|---|---|
| `org_center_schema.sqlx` | operations, tag `dimension_daily` | `CREATE SCHEMA IF NOT EXISTS org_center` — same bootstrap as `pub_sub_schema` / `cdc_schema` |
| `org_center_unit.sqlx` | table | 1 row = 1 unit (division / region / section) |
| `org_center_member.sqlx` | table | 1 row = 1 person in one position at one unit for a date range |
| `org_center_person.sqlx` | table | 1 row = 1 person (across companies), built from `org_center_member` |
| `org_center_link.sqlx` | table | 1 row = 1 PC linked to 1 TA at 1 branch for a date range, from `mds_data_pc_ta` (0 rows while MDS is empty) |

`org_center_unit` and `org_center_member` depend on `org_center_schema`, the `dim_*_last` tables they read, and
`update_sk_sale_rep_group` — the `_last` tables are built with NULL `DirectorSK` /
`RegionSK` / `SectionSK`, and that step fills them
([special-cases](../dimension/special-cases.md#update_sk_sale_rep_group--imperative-update-step)).
`org_center_person` depends on `org_center_schema` and `org_center_member` only.
`org_center_link` depends on `org_center_schema` only. `org_center_member` also depends on `org_center_link` (PC rows).

## Org levels (3)

| depth | unit_level | Thai | Source | unit_code | parent |
|---:|---|---|---|---|---|
| 1 | `DIVISION` | ฝ่าย | `dim_director_last` | `DirectorID` | — (NULL) |
| 2 | `REGION` | ภาค | `dim_region_last` | `SubRegionID` | division via `DirectorSK` |
| 3 | `SECTION` | ส่วน | `dim_section_last` | `SectionID` | region via `RegionSK` |

The TA app's "team" = section. Department (เขต) is **not** a level: a TA's departments
are listed in `org_center_member.department_ids`.

`unit_id` = prefix + code: `DIR-00001`, `REG-NE`, `SEC-NE1`. The prefix keeps codes
from colliding across levels.

**Region code is `SubRegionID`, not `RegionID`**: region `PS1` has five sub-regions
(`PS1-1` … `PS1-5`), each its own `dim_region_last` row, so `RegionID` would give five
rows the same `unit_id`. For every other region `SubRegionID = RegionID`.

## `org_center_unit`

Key: `company_id` + `unit_id`.

| Column | Type | Source |
|---|---|---|
| `company_id` | STRING | `companyID` of the dim |
| `unit_id` | STRING | `DIR-` / `REG-` / `SEC-` + `unit_code` |
| `unit_level` | STRING | `DIVISION` / `REGION` / `SECTION` |
| `depth` | INT64 | 1 / 2 / 3 |
| `unit_code` | STRING | `DirectorID` / `SubRegionID` / `SectionID` |
| `unit_name` | STRING | `DirectorName` / `RegionName` / `SectionName` |
| `parent_unit_id` | STRING | NULL for a division |
| `valid_from` / `valid_to` | DATE | `StartDate` / `EndDate` of the `_last` row (`2066-12-31` = still active) |

## `org_center_member`

Key: `company_id` + `employee_id` + `position_code` + `unit_id` + `valid_from`.

| Column | Type | Source |
|---|---|---|
| `company_id` | STRING | `companyID` |
| `employee_id` | STRING | MDS employee code (the TA app's `person_key`); PC rows use the link's `pc_employee_id` |
| `first_name` / `last_name` / `nickname` | STRING | the dim of that position; for PCs, see below |
| `email` | STRING | `mds_data_org_employee_mapping_center.employeeemail` — NULL when the person is not in that table |
| `position_code` | STRING | `DIRECTOR` / `REGION_MGR` / `SECTION_MGR` / `TA` / `PC_MDT` / `PC_AGENT` |
| `unit_id` | STRING | the unit the position is held at |
| `department_ids` | ARRAY&lt;STRING&gt; | TA departments merged into the row; empty for managers and PCs |
| `valid_from` / `valid_to` | DATE | inclusive membership interval: dim `StartDate` / `EndDate`; for a TA, earliest start to latest end over the merged departments; for PCs, see below |

**PC rows** (`PC_MDT` / `PC_AGENT`, from `org_center_link`): position = the link's `pc_type`; names from
`mds_data_mdt_sales_pc_master` (active rows; latest `end_date`, then `start_date`, then `updated_at`, then lowest `id`; no nickname).
A link with NULL `pc_type` or NULL `pc_employee_id`, or no overlapping TA row, produces no PC member row.
Unit = the unit of the linked TA's `TA` member row in the same
company whose dates overlap the link period; dates = the overlap (link `valid_to` is exclusive, so one day
earlier unless `2066-12-31`). If the TA has exactly one overlapping unit, the PC takes it. If the TA has more
than one (41 of 180 TAs on 2026-10-30, all ag01), only the unit whose `department_ids` has a `_`-separated segment
exactly equal to the `zone_id` of the PC's branch (`mds_data_mdt_sales_branch_master.branch_code`) is kept; no match =
no member row (the link row stays). For each company + person + PC type + unit, overlapping or adjacent
periods across branches and TAs merge into one contiguous interval. Disjoint periods stay in separate rows;
`valid_from` distinguishes those rows, so gaps do not make the person active in `org_center_person`.
No phone number in member — it is in `org_center_person`.

| position_code | Source | unit | Names |
|---|---|---|---|
| `DIRECTOR` | `dim_director_last.DirectorOfSalesID` | `DIR-<DirectorID>` | `DirectorOfSalesName` split: first word = first name, rest = last name, no nickname |
| `REGION_MGR` | `dim_region_manager_last.RegionManagerEmployeeID` | `REG-<SubRegionID>` | `RegionManagerName` / `Surname` / `Nickname` |
| `SECTION_MGR` | `dim_section_manager_last.SectionManagerEmployeeID` | `SEC-<SectionID>` | `SectionManagerName` / `Surname` / `Nickname` |
| `TA` | `dim_sale_representative_last`, **only `DepartmentID IS NOT NULL`** (rows from MDS, not the ledger) | `SEC-` + the section of the TA's department (`SectionSK`) | `EmployeeName` / `Surname` / `Nickname` of the row with the latest `EndDate` |

TA rows are grouped by company + employee + section. A TA whose departments sit in
several sections gets one row per section (on 2026-10-29: 139 active TAs in 1 section,
40 in 2–18 sections — mostly MDT store-chain sections). Rows whose `employee_id` is
NULL are dropped (one region manager slot, `Other`).

Email: active rows of the mapping table, one per `employeeid` (a non-NULL email
first, then the latest `updated_at`).

## `org_center_person`

Key: `employee_id` — one row per person, even when the person is in two companies.
The who-is-who list (the TA app's `employees`); `org_center_member` stays the
where-they-sit list with dates (the app's `appointments`). No boss column: the direct
boss of a DIRECTOR / REGION_MGR / SECTION_MGR / TA is the manager of the parent unit
(`org_center_unit.parent_unit_id` → `org_center_member`).

| Column | Type | Source |
|---|---|---|
| `employee_id` | STRING | `org_center_member.employee_id` (never NULL) |
| `first_name` / `last_name` / `nickname` | STRING | picked from the person's member rows (rule below) |
| `email` | STRING | the member-row email (rule below); only when empty, `mds_data_employee_info.Email` |
| `mobile_phone` | STRING | `mds_data_employee_info.MobilePhone` by `EmployeeID` (active rows, as entered); NULL when absent |
| `company_ids` | ARRAY&lt;STRING&gt; | every `company_id` of the person's member rows, sorted |
| `position_codes` | ARRAY&lt;STRING&gt; | distinct positions with a member row valid today, in order `DIRECTOR`, `REGION_MGR`, `SECTION_MGR`, `TA`, `PC_MDT`, `PC_AGENT`; empty when none is valid |
| `is_active` | BOOL | the person has a member row valid today |

"Valid today" = `CURRENT_DATE('Asia/Bangkok') BETWEEN valid_from AND valid_to`.

**Name / email pick rule** (deterministic). Row order: among the person's member rows
valid today, the highest position (`DIRECTOR` > `REGION_MGR` > `SECTION_MGR` > `TA` > `PC_MDT` > `PC_AGENT`), then
the latest `valid_to`, then the lowest `company_id`. If no row is valid today, the row
with the latest `valid_to` (then `company_id`). Remaining ties go to the higher position,
then the lowest `unit_id`.

- `email`: the first non-NULL member email in that order (email is joined per `employee_id`,
  so every row carries the same value); its fallback source is listed above.
- `nickname`: the first non-NULL `nickname` in that order (`DIRECTOR` rows have none).
- `first_name` / `last_name`: the first non-`DIRECTOR` row in that order, because those
  rows have real separate name and surname fields. Only a person with no non-`DIRECTOR`
  row gets the `DIRECTOR` name, split at the first space.

`mds_data_employee_info` is filtered to active rows, picking the latest `updated_at`, then lowest `id`,
per `EmployeeID`. Both contact fields are kept as entered. Contact-only employees do not create person rows.

Placeholder managers (`Non Director`, `9999990`–`9999999`)
get a row like any other person.

Checks before the first build (2026-10-29, read-only SELECT): 206 rows = 206 distinct
`employee_id` in `org_center_member`, 0 duplicate `employee_id`, every member
`employee_id` present, 201 `is_active` = 201 people with a member row valid today,
8 people in two companies (`ab01` + `ag01`), email NULL for 171.

## `org_center_link`

Key: `company_id` + `pc_employee_id` + `branch_type` + `branch_code` + `valid_from` (the MDS key). Mirrors the
TA app's `member_links` with `link_type = 'PC_TA'`: from = PC, to = TA, site = `branch_code`.

Rows = `mds_dataset.mds_data_pc_ta` with `is_active = TRUE`, values **as entered** (no trim, case change,
dedupe or filtering of unknown codes; wrong codes are fixed in MDS, not here). **0 rows while the MDS table is
empty.**

| Column | Type | Source |
|---|---|---|
| `company_id` | STRING | `companyID` |
| `link_type` | STRING | always `PC_TA` |
| `pc_employee_id` | STRING | `PCEmployeeID` |
| `pc_type` | STRING | `mds_data_mdt_sales_pc_master.employee_type`: NULL or empty string → `PC_MDT`, `พันธมิตร` → `PC_AGENT`; other value or PC not in the active master → NULL; master row selected as described under PC member rows |
| `branch_code` | STRING | `BranchCode` |
| `branch_type` | STRING | `BranchType` |
| `ta_employee_id` | STRING | `TAEmployeeID` |
| `valid_from` / `valid_to` | DATE | `StartDate` / `EndDate`; `EndDate` is the first day the TA is **no longer** responsible (exclusive); empty = `2066-12-31` |

Source rule (checked by the MDS team on load): one valid row per
`(companyID, PCEmployeeID, BranchType, BranchCode)` per day — periods never overlap.

## Rules

- **Expired rows are kept.** Date derivation is described per table above; the consumer
  decides who is active. Placeholder managers from MDS (`Non Director`, `9999990`–
  `9999999` such as `HO`, `Online`, `Imboon`) are passed through too.
- Dim-sourced units and memberships use only `_last` data: latest row per code. PC link periods
  come from active MDS assignments as described above. History after go-live is the consumer's job.
- Known gap (accepted 2026-10-29): 7 MDS assignments of 2 people (`1053148` on 6 cost
  channels `BT/DH/GB/HP/MH/TW_001`, `1052088` on `N2_TA01`) are not in
  `dim_sale_representative_last`, so they are not in org center.

## Checks run before the first build (2026-10-29, read-only SELECT of both tables)

| Check | Result |
|---|---|
| Units per level | DIVISION 9 · REGION 28 · SECTION 127 (expired 1 / 1 / 4) |
| Members per position (rows / distinct people) | DIRECTOR 9/7 · REGION_MGR 27/15 · SECTION_MGR 127/29 · TA 440/180 |
| Duplicate keys | 0 in both tables |
| Every `parent_unit_id` and member `unit_id` exists in `org_center_unit` | 0 missing |
| Active TA people vs MDS active TA people (by company + employee) | 175 = 175, no difference; by department only the 7 known assignments differ |
| 29 Sales users of `view_rls_sale_data`: Director / Region / Section values derived from org center | identical for all 29 |
| Rows with a future `valid_from` | 0 |

## Not in this round

- Per-system RLS views (Power BI, TA app) and read grants for the backend team.
- Changing the TA spec from 4 levels to 3.

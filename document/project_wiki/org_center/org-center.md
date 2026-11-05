# Org Center — `org_center_unit` / `org_center_member` / `org_center_person` / `org_center_link` / `org_center_customer_ta` / `org_center_exception` / `org_center_flags`

> **LLM context**: Dataset `org_center` (`databuffet.ORG_CENTER`), folder
> `definitions/org_center/`, added 2026-10-29 for the TA AI Assistant. It is the single
> source of **who sits in which unit and position, TA customer portfolios, and special access exceptions**; Power BI RLS, the TA app and other
> systems consume it; TA customer access is precomputed by
> [`rls_ta_customer`](../cdc-process/process.md#rls_ta_customersqlx--ta-customer-access-who-sees-which-customer). All seven tables are `type: "table"`,
> tag `dimension_daily`, rebuilt every night (`org_center_unit` and `org_center_member` after
> `update_sk_sale_rep_group`; `org_center_person` after `org_center_member`). For PC → TA assignments, see the
> [table contract](../../okf/org_center/org_center_link.md).
> For TA customer portfolios, see the [table contract](../../okf/org_center/org_center_customer_ta.md).
> They carry **business codes, not SKs**, so consumers can keep them across days.

The TA app is planned to derive sales visibility from these org-center units,
memberships (appointments), and special-access exceptions.

## Files

| File | Type | What it does |
|---|---|---|
| `org_center_schema.sqlx` | operations, tag `dimension_daily` | `CREATE SCHEMA IF NOT EXISTS org_center` — same bootstrap as `pub_sub_schema` / `cdc_schema` |
| `org_center_unit.sqlx` | table | 1 row = 1 unit (company / division / region / section) |
| `org_center_member.sqlx` | table | 1 row = 1 person in one position at one unit for a date range |
| `org_center_person.sqlx` | table | 1 row = 1 person (across companies), built from `org_center_member` |
| `org_center_link.sqlx` | table | PC-to-TA assignments — [table contract](../../okf/org_center/org_center_link.md) |
| `org_center_customer_ta.sqlx` | table | TA customer portfolios — [table contract](../../okf/org_center/org_center_customer_ta.md) |
| `org_center_exception.sqlx` | table | 1 row = 1 person x company x product scope of a special access exception, from `mds_data_org_rls_special` (see [`org_center_exception`](#org_center_exception)) |
| `org_center_flags.sqlx` | table | 1 row = 1 data-quality problem; checked tables and MDS sources are listed in the [flags card](../../okf/org_center/org_center_flags.md#how-it-is-built) (rules below under [`org_center_flags`](#org_center_flags)) |

`org_center_unit` and `org_center_member` depend on `org_center_schema`, the `dim_*_last` tables they read, and
`update_sk_sale_rep_group` — the `_last` tables are built with NULL `DirectorSK` /
`RegionSK` / `SectionSK`, and that step fills them
([special-cases](../dimension/special-cases.md#update_sk_sale_rep_group--imperative-update-step)).
`org_center_person` depends on `org_center_schema` and `org_center_member` only.
`org_center_link` depends on `org_center_schema` only. `org_center_unit` also depends on `dim_company` (company name). Exception and flags build dependencies are listed in their [exception](../../okf/org_center/org_center_exception.md#how-it-is-built) and [flags](../../okf/org_center/org_center_flags.md#how-it-is-built) cards. `org_center_member` also depends on `org_center_link` (PC rows).

## Org levels (4)

| depth | unit_level | Thai | Source | unit_code | parent |
|---:|---|---|---|---|---|
| 0 | `COMPANY` | บริษัท | `mds_data_company_master` (latest active row per cleaned `CompanyID`) | `CompanyID` | — (NULL) |
| 1 | `DIVISION` | ฝ่าย | `dim_director_last` | `DirectorID` | company via `CO-<company_id>` |
| 2 | `REGION` | ภาค | `dim_region_last` | `SubRegionID` | division via `DirectorSK` |
| 3 | `SECTION` | ส่วน | `dim_section_last` | `SectionID` | region via `RegionSK` |

The TA app's "team" = section. Department (เขต) is **not** a level: a TA's departments
are listed in `org_center_member.department_id`.

`unit_id` = prefix + code: `CO-ag01`, `DIR-00001`, `REG-NE`, `SEC-NE1`. The prefix keeps codes
from colliding across levels.

**Region code is `SubRegionID`, not `RegionID`**: region `PS1` has five sub-regions
(`PS1-1` … `PS1-5`), each its own `dim_region_last` row, so `RegionID` would give five
rows the same `unit_id`. For every other region `SubRegionID = RegionID`.

## `org_center_unit`

Key: `company_id` + `unit_id`.

| Column | Type | Source |
|---|---|---|
| `company_id` | STRING | cleaned `CompanyID` from MDS for COMPANY; `companyID` of the dim otherwise |
| `unit_id` | STRING | `CO-` / `DIR-` / `REG-` / `SEC-` + `unit_code` |
| `unit_level` | STRING | `COMPANY` / `DIVISION` / `REGION` / `SECTION` |
| `depth` | INT64 | 0 / 1 / 2 / 3 |
| `unit_code` | STRING | `CompanyID` / `DirectorID` / `SubRegionID` / `SectionID` |
| `unit_name` | STRING | `CompanyNameTH` / `DirectorName` / `RegionName` / `SectionName` |
| `parent_unit_id` | STRING | NULL for COMPANY; company for DIVISION; division for REGION; region for SECTION |
| `valid_from` / `valid_to` | DATE | COMPANY: `2000-01-01` / `2066-12-31`; otherwise `StartDate` / `EndDate` of the `_last` row (`2066-12-31` = still active) |
| `plan_code` | STRING | the unit's code in `Org_Mock_Master_Plan_v4.xlsx` (below); `unit_id` / `unit_code` are unchanged |
| `company_name` | STRING | COMPANY: cleaned MDS `CompanyNameTH`; otherwise `dim_company.CompanyNameTH` by `company_id` (NULL if absent) |

For the `region_code` column used by TA customer access, see the authoritative
[`org_center_unit` schema](../../okf/org_center/org_center_unit.md#schema).

**`plan_code`** (added 2026-10-30; the plan file's codes differ from the live codes in two places):

- COMPANY: NULL.
- DIVISION: `DirectorID`.
- REGION: `dim_region_last.RegionID` — the five `PS1-n` sub-regions all map to `PS1`; every other region equals `unit_code`.
- SECTION: `unit_code`, except 7 Dummy sections that the plan names by their name: `Dummy999994`→`HO`, `Dummy999993`→`Imboon`, `Dummy999991`→`Online`, `Dummy999992`→`IMP1`, `Dummy999992_02/03/04`→`IMP2/3/4`. This is a fixed list in `org_center_unit.sqlx` (`planSectionCode`), because no Data Mart column holds it; add a row there if the plan adds one.

## `org_center_member`

Key: `company_id` + `employee_id` + `position_code` + `unit_id` + `valid_from`.

See the [table card](../../okf/org_center/org_center_member.md#schema) for the authoritative schema and column sources.

**PC rows** (`PC_MDT` / `PC_AGENT`, from `org_center_link`): position = the link's `pc_type`; names from
`mds_data_mdt_sales_pc_master` (active rows; latest `end_date`, then `start_date`, then `updated_at`, then lowest `id`; no nickname).
A link with NULL `pc_type`, NULL `pc_employee_id` or NULL `department_id`, or a department with no overlapping TA seat, produces no PC member row.
TA binding is by department (the TA position): the PC takes the unit of the TA seat of `link.department_id` in the same
company (one department = one unit; any TA seated in that department gives the seat, so moving a TA changes nothing here);
dates = the overlap of the link period and the seat (link `valid_to` is exclusive, so one day
earlier unless `2066-12-31`). For each company + person + PC type + unit, overlapping or adjacent
periods across branches and departments merge into one contiguous interval. Disjoint periods stay in separate rows;
`valid_from` distinguishes those rows, so gaps do not make the person active in `org_center_person`.
No phone number in member — it is in `org_center_person`.

| position_code | Source | unit | Names |
|---|---|---|---|
| `CEO` | `mds_data_company_master.CEOEmpID` (active row, latest `updated_at`, then lowest `id`, per cleaned `CompanyID`) | `CO-<company_id>` | cleaned `CEOName` split like `DIRECTOR`; no nickname |
| `DIRECTOR` | `dim_director_last.DirectorOfSalesID` | `DIR-<DirectorID>` | `DirectorOfSalesName` split: first word = first name, rest = last name, no nickname |
| `REGION_MGR` | `dim_region_manager_last.RegionManagerEmployeeID` | `REG-<SubRegionID>` | `RegionManagerName` / `Surname` / `Nickname` |
| `SECTION_MGR` | `dim_section_manager_last.SectionManagerEmployeeID` | `SEC-<SectionID>` | `SectionManagerName` / `Surname` / `Nickname` |
| `TA` | `dim_sale_representative_last`, **only `DepartmentID IS NOT NULL`** (rows from MDS, not the ledger) | `SEC-` + the section of the TA's department (`SectionSK`) | `EmployeeName` / `Surname` / `Nickname` of the row with the latest `EndDate` |

TA rows are grouped by company + employee + section. A TA whose departments sit in
several sections gets one row per section. Rows whose `employee_id` is
NULL are dropped (one region manager slot, `Other`).

`CEO` rows: one row per company on its COMPANY unit, including companies without divisions. Each DIVISION points to that COMPANY unit, so its DIRECTOR resolves the CEO through the parent-unit lookup. No CEO member row (and no person created from that seat) while cleaned `CEOEmpID` is empty; an empty `CEOName` does not suppress the seat.

Email: active rows of the mapping table, one per `employeeid` (a non-NULL email
first, then the latest `updated_at`).

## `org_center_person`

Key: `employee_id` — one row per person, even when the person is in two companies.
The who-is-who list (the TA app's `employees`); `org_center_member` stays the
where-they-sit list with dates (the app's `appointments`). No boss column: the direct
boss of a DIRECTOR / REGION_MGR / SECTION_MGR / TA is the manager of the parent unit
(`org_center_unit.parent_unit_id` → `org_center_member`).

See the [table card](../../okf/org_center/org_center_person.md#schema) for the authoritative schema and column sources.

"Valid today" = `CURRENT_DATE('Asia/Bangkok') BETWEEN valid_from AND valid_to`.

**Name / email pick rule** (deterministic). Row order: among the person's member rows
valid today, the highest position (`CEO` > `DIRECTOR` > `REGION_MGR` > `SECTION_MGR` > `TA` > `PC_MDT` > `PC_AGENT`), then
the latest `valid_to`, then the lowest `company_id`. If no row is valid today, the row
with the latest `valid_to` (then `company_id`). Remaining ties go to the higher position,
then the lowest `unit_id`.

- `email`: the first non-NULL member email in that order (email is joined per `employee_id`,
  so every row carries the same value); its fallback behavior is defined in the [person schema](../../okf/org_center/org_center_person.md#schema).
- `nickname`: the first non-NULL `nickname` in that order (`CEO` and `DIRECTOR` rows have none).
- `first_name` / `last_name`: the first row that is not `CEO` / `DIRECTOR` in that order, because those
  rows have real separate name and surname fields. Only a person with no such row
  gets the `DIRECTOR` name, then the `CEO` name (full name split at the first space), so a CEO already in the table keeps the existing name.

The [person card](../../okf/org_center/org_center_person.md) owns contact-source selection, pass-through values and the exclusion of contact-only employees.

Placeholder managers (`Non Director`, `9999990`–`9999999`)
get a row like any other person.

## `org_center_link`

See the [table card](../../okf/org_center/org_center_link.md) for the source, grain, schema, pass-through and overlap constraints, rebuild behavior and date-filter example.

## `org_center_customer_ta`

See the [table card](../../okf/org_center/org_center_customer_ta.md) for the source, grain, schema, rebuild behavior and date-filter example.

## `org_center_exception`

The [OKF card](../../okf/org_center/org_center_exception.md) owns the grain, schema, source filtering, list expansion and rebuild contract. Missing-employee checks are described under [`org_center_flags`](#org_center_flags).

## `org_center_flags`

1 row = 1 problem, rebuilt every night. Report only (input = output): nothing in the other tables is
fixed or hidden; fix the source (MDS) and the row disappears on the next run. Rules follow the Check sheet of
`Org_Mock_Master_Plan_v4.xlsx`, only the ones that fit this design. Not built: Approved HC (no source),
LINE UUID (no check rule; see the [person schema](../../okf/org_center/org_center_person.md#schema) for its MDS source), "more than 1 current team assignment" (a TA in several sections is valid).

| Column | Type | Meaning |
|---|---|---|
| `company_id` | STRING | NULL for person-level rules |
| `entity` | STRING | `UNIT` / `MEMBER` / `PERSON` / `LINK` / `CUSTOMER_TA` / `COMPANY` / `EXCEPTION` |
| `entity_key` | STRING | JSON array of the entity's key components, preserving NULL as JSON null (company: company_id · unit: company, unit_id · member: its 5 key columns · person: employee_id · link: its 5 key columns · customer_ta: company_id, customer_code, department_id, valid_from · exception: source_row_id, company_code, marketing_group_id, sub_marketing_id, segment_id; dates are ISO strings) |
| `rule_code` | STRING | see below |
| `rule_description` | STRING | Thai description |

| `rule_code` | Entity | Raised when |
|---|---|---|
| `DUPLICATE_ID` | UNIT / MEMBER / PERSON / LINK | the table's key appears more than once |
| `MEMBER_NO_PERSON` | MEMBER | `employee_id` not in `org_center_person` |
| `MEMBER_NO_UNIT` | MEMBER | `unit_id` not in `org_center_unit` for that company |
| `UNIT_NO_PARENT` | UNIT | DIVISION / REGION / SECTION whose `parent_unit_id` is not a unit of the same company |
| `UNIT_NO_MANAGER` | UNIT | DIVISION / REGION / SECTION valid today with no `DIRECTOR` / `REGION_MGR` / `SECTION_MGR` (by level) member valid today |
| `COMPANY_NO_CEO` | COMPANY | an active company in `mds_data_company_master` has an empty cleaned `CEOEmpID` in its latest active row (`updated_at` descending, then lowest `id`); includes companies without divisions |
| `PC_TA_UNKNOWN_PC` | LINK | `pc_employee_id` not in active `mds_data_mdt_sales_pc_master` |
| `UNKNOWN_DEPARTMENT` | LINK / CUSTOMER_TA | `department_id` is set but no `TA` member row of that company has it in `department_id` |
| `NO_DEPARTMENT` | LINK / CUSTOMER_TA | `department_id` is empty (department not yet known): the PC gets no member row; the customer gives no access in `rls_ta_customer` |
| `PC_TA_UNKNOWN_BRANCH` | LINK | `PC_MDT` link whose `branch_code` is not in active `mds_data_mdt_sales_branch_master` (the master is MDT only) |
| `PC_TA_OVERLAP` | LINK | another row of the same company + PC + `branch_type` + `branch_code` overlaps in `[valid_from, valid_to)` with different departments or start dates — one flag per affected link row, regardless of how many counterparts overlap |
| `EXCEPTION_NO_EMPLOYEE` | EXCEPTION | a row of `org_center_exception` has no `employee_id`; one flag per expanded company and product scope |
| `PHONE_FORMAT` | PERSON | non-NULL `mobile_phone` matches neither `0xx-xxx-xxxx` nor `+66` followed by 1–2 digits, 3 digits, and 4 digits, with an optional space or hyphen between each group (including after `+66`) |
| `PHONE_DUPLICATE` | PERSON | the same `mobile_phone` belongs to more than one person |

COMPANY units are excluded from `UNIT_NO_MANAGER`; missing CEOs are covered by `COMPANY_NO_CEO`.

## CEO

Added 2026-10-30 after MDS Company Master got optional CEO fields, following `Org_Mock_Master_Plan_v4.xlsx` (sheets M00_Company / M02_Position). The Excel CEO values are mock; MDS supplies the real assignments later. See [`org_center_member`](#org_center_member) for the seat contract, [org levels](#org-levels-4) for the hierarchy, and [`org_center_flags`](#org_center_flags) for missing-CEO checks.

## Rules

- **MDS cutover prerequisite:** do not merge this department-binding change before the MDS swap. TA_PC must provide optional DepartmentID with its existing key; TA_CUSTOMER must be recreated under the same name with key companyID + CustomerCode + optional DepartmentID + StartDate. TAEmployeeID is removed from both sources. Fast-forwarding `nonprod` and rebuilding require a separate go-ahead after the swap.
- **Expired rows are kept.** Date derivation is described per table above; the consumer
  decides who is active. Placeholder managers from MDS (`Non Director`, `9999990`–
  `9999999` such as `HO`, `Online`, `Imboon`) are passed through too.
- Dim-sourced units and memberships use only `_last` data: latest row per code. PC link periods
  come from active MDS assignments as described above. History after go-live is the consumer's job.
- Known gap (accepted 2026-10-29): 7 MDS assignments of 2 people (`1053148` on 6 cost
  channels `BT/DH/GB/HP/MH/TW_001`, `1052088` on `N2_TA01`) are not in
  `dim_sale_representative_last`, so they are not in org center.

## Not in this round

- Power BI RLS views and read grants for the backend team. TA customer access is built (`rls_ta_customer`, exported by `export_rls_ta_customer`) and the TA app tables are exported by the Pub/Sub export views.
- Changing the TA spec from 4 levels to 3.

#!/usr/bin/env python3
"""Deploy real invoice, customer-report and fact actions to a disposable local BigQuery server.

Input tables are fixtures; the transformations, UDFs and Dataform materializations
are the repository's executable actions. No ADC or remote endpoint is used.
Requires Dataform CLI/core 3.0.0 and a fresh loopback BigQuery emulator.
"""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from test_customer_report_info_live import PROJECT, compatibility_transport


def fields(*, strings="", integers="", floats="", dates="", datetimes="", booleans="", timestamps=""):
    schema = {}
    for names, kind in ((strings, "STRING"), (integers, "INTEGER"), (floats, "FLOAT"),
                        (dates, "DATE"), (datetimes, "DATETIME"), (booleans, "BOOLEAN"),
                        (timestamps, "TIMESTAMP")):
        schema.update(dict.fromkeys(names.split(), kind))
    return schema


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--quoted-udf-workaround", action="store_true")
    parser.add_argument("--base", default="350ebecd6ff394acf55023c2b30c551b8c28c18d",
                        help="commit whose fact view reproduces the missing customer-mapping regression")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    scratch = args.scratch.resolve()
    if not scratch.is_relative_to(repo):
        parser.error("scratch directory must be inside the worktree")
    if urllib.parse.urlparse(args.endpoint).hostname not in ("127.0.0.1", "localhost"):
        parser.error("only a disposable loopback BigQuery server is allowed")
    scratch.mkdir(parents=True, exist_ok=True)
    args.evidence.mkdir(parents=True, exist_ok=True)
    endpoint = args.endpoint.rstrip("/")
    if args.quoted_udf_workaround:
        endpoint = compatibility_transport(endpoint, args.evidence,
                                           ("clean_company_prefix", "fn_get_scg_customer_ids", "fn_flag_scg", "fn_flag_exc"))
    responses, transcripts, checks = [], [], []

    def api(path, body=None):
        request = urllib.request.Request(
            f"{endpoint}/bigquery/v2/projects/{PROJECT}/{path}",
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(error.read().decode()) from error

    def query(sql):
        response = api("queries", {"query": sql, "useLegacySql": False})
        responses.append({"query": sql, "response": response})
        (args.evidence / "query-responses.json").write_text(json.dumps(responses, ensure_ascii=False, indent=2))
        if response.get("errors"):
            raise RuntimeError(response["errors"])
        assert response.get("jobComplete"), response
        schema = response.get("schema", {}).get("fields", [])
        rows = []
        for row in response.get("rows", []):
            decoded = {}
            for field, cell in zip(schema, row["f"]):
                value = cell.get("v")
                if value is not None and field["type"] in ("INTEGER", "INT64"):
                    value = int(value)
                elif value is not None and field["type"] in ("FLOAT", "FLOAT64"):
                    value = float(value)
                decoded[field["name"]] = value
            rows.append(decoded)
        return rows

    today = dt.date.fromisoformat(query("SELECT CURRENT_DATE('Asia/Bangkok') AS today")[0]["today"])
    day = today - dt.timedelta(days=2)
    tables = {}

    def table(dataset, name, schema, rows=()):
        tables[(dataset, name)] = {"schema": schema, "rows": list(rows)}
        return tables[(dataset, name)]["rows"]

    table("dimension_table", "dim_company", fields(strings="companyID", integers="CompanySK"),
          [{"CompanySK": 1, "companyID": "ag01"}, {"CompanySK": 2, "companyID": "aa05"}])
    table("dimension_table", "dim_calendar", fields(dates="Date"),
          [{"Date": str(day)}, {"Date": str(day + dt.timedelta(days=1))}])
    common = fields(
        strings="DepartmentID DepartmentName SectionID SectionName RegionID SubRegionID RegionName DirectorID DirectorName "
                "SectionManagerEmployeeID SectionManagerName SectionManagerSurname SectionManagerNickname "
                "RegionManagerEmployeeID RegionManagerName RegionManagerSurname RegionManagerNickname "
                "EmployeeID EmployeeName EmployeeSurname EmployeeNickname companyID ChangeSectionFlag CostChannelID "
                "DepCode CustomerFlag ProvinceID DummyChannel MarketingGroupID status rebate salesExc accExc "
                "customerCode newSectionID milStk ProductCode ProductMac5Description",
        integers="CompanySK DepartmentSK SectionSK RegionSK DirectorSK SectionManagerSK RegionManagerSK SaleRepSK "
                 "ChannelSK CostStkSk CostGroupSK StkMktSK ReportSK PumpSK",
        floats="Percent", dates="StartDate EndDate startDate endDate", booleans="FlagNewProductMKT")
    # StartDate/startDate are the same identifier in GoogleSQL.
    common.pop("startDate")
    common.pop("endDate")
    for name in ("dim_department_last", "dim_sale_representative_last", "dim_section_last", "dim_region_last",
                 "dim_section_manager_last", "dim_region_manager_last", "dim_director_last", "dim_rebate", "dim_report",
                 "dim_section", "dim_region", "dim_director", "dim_sale_representative", "dim_channel",
                 "dim_change_district", "dim_cost_stk", "dim_cost_group", "dim_stk_mkt", "dim_region_manager",
                 "dim_section_manager", "dim_product_master", "dim_pump_information"):
        table("dimension_table", name, common)
    table("dimension_table", "dim_aging", fields(strings="CFSvnosID", integers="CompanySK AgingSK"))
    table("dimension_view", "view_dim_aging", fields(strings="cfsVnosID", integers="CompanySK AgingSK AgingRangSK"))
    table("dimension_table", "dim_order", fields(strings="mihVnos", integers="CompanySK OrderSK"))
    table("mds_dataset", "mds_data_customer_segment_master", fields(
        strings="companyID Segment1 Segment2 Segment3 DescriptionThai DescriptionEng SortOrder id", booleans="is_active"),
        [{"companyID": "ag01", "Segment1": "Gold", "Segment2": "Gold", "Segment3": "GOLD", "SortOrder": "1",
          "id": "gold", "is_active": True}])
    table("mds_dataset", "mds_data_customer_report_master", fields(
        strings="companyID CustomerReportName CustomerTier ShopOnline OnlinePercent id DepartmentID",
        booleans="FlagPC is_active", timestamps="updated_at"),
        [{"companyID": "ag01", "CustomerReportName": "Named Shop", "CustomerTier": "GOLD", "id": "named",
          "OnlinePercent": "12.5", "is_active": True, "updated_at": f"{today}T00:00:00Z"},
         {"companyID": "ag01", "CustomerReportName": "ไม่ระบุชื่อ ลูกค้า", "CustomerTier": "GOLD", "id": "reserved-like",
          "DepartmentID": "TA_MDS", "OnlinePercent": "80", "is_active": True, "updated_at": f"{today}T00:00:00Z"}])
    table("mds_dataset", "mds_data_crc_shop_name_rename", fields(
        strings="crc_shop_name crc_shop_name_change", booleans="is_active"))
    table("validated_mac5", "mec", fields(strings="meccode company_id mecdesc"))
    table("validated_mac5", "tbook_quotation", fields(
        strings="company_id agent1 channel id", datetimes="dinsert"))
    table("onetime", "mapping_invoice", fields(strings="milPer milVnos CompanyID SectionID", booleans="FlagMustUser"))
    customers = table("dimension_view", "view_dim_customer", fields(
        strings="companyID debcode debnamet NicknameCustomer", integers="CompanySK", booleans="FlagMDSNickName"))
    debs = table("validated_mac5", "deb", fields(strings="company_id debcode debsalesp debgroup", datetimes="debdate"))
    invoice_schema = fields(strings="companyID mihType mihVnos mihCus milLinkvcno mihNotes mihMec mihPer mihDep",
                            integers="CompanySK InvoiceSK OrderSK mihCancel mihStatus", datetimes="mix_date")
    invoices = table("dimension_table", "dim_invoice", invoice_schema)
    cases = [(1, "NAMED", "บริษัท Named Shop จำกัด"), (1, "PREFIX", "บริษัท"),
             (1, "LIMITED", "ห้างหุ้นส่วนจำกัด"), (1, "NULL_NAME", None),
             (1, "111020730.", None), (2, "NAMED_OTHER", "Named Shop")]
    for sk, (company_sk, code, name) in enumerate(cases, 1):
        company = "ag01" if company_sk == 1 else "aa05"
        if code != "111020730.":
            customers.append({"CompanySK": company_sk, "companyID": company, "debcode": code,
                              "debnamet": name, "FlagMDSNickName": False})
            debs.append({"company_id": company, "debcode": code, "debdate": f"{day} 00:00:00"})
        invoices.append({"CompanySK": company_sk, "companyID": company, "InvoiceSK": sk,
                         "mihType": "IS", "mihVnos": code, "mihCus": code, "mihCancel": 0, "mihStatus": 0,
                         "mix_date": f"{day} 10:00:00"})

    amount_names = ("milQuan milQuanp2 milAdisc milCog milConv milDisca milDisct milVat milSum milExchg milAcost "
                    "milCost milUcost milUprice Vat milsum_incvat mildisca_incvat milcog_incvat "
                    "DepositExcVat DepositIncVat DepositVat")
    transactions = table("fact_table", "fact_transcation", fields(
        strings="companyID milVnos milType milCus milStk milPer milDep milLinkvcno milDesc DummyChannel ChannelCostID",
        integers="CompanySK SaleRepSK SectionSK SectionManagerSK RegionSK RegionManagerSK DirectorSK ChangeSectionSK "
                 "ChangeRegionSK ChangeDirectorSK ChangeSectionManagerSK ChangeRegionManagerSK CostStkSk CostGroupSK "
                 "StkMktSK ChannelSK OrderProvinceSK milYear milMonth milDay milListno mihCancel mihStatus",
        floats=amount_names, dates="mix_date", booleans="FlagNewProductMKT"))
    fact_schema = fields(strings="milVnos milType milCus milStk milLinkvcno",
                         integers="CompanySK milYear milMonth milDay FactInvoiceSK InvoiceSK OrderSK FactOrderSK "
                                  "QuotationSK FactQuotationSK")
    facts = table("fact_table", "fact_invoice", fact_schema)
    table("fact_table", "fact_order", fact_schema)

    def transaction(company_sk, code, invoice_sk):
        row = {"CompanySK": company_sk, "companyID": "ag01" if company_sk == 1 else "aa05",
               "milYear": day.year, "milMonth": day.month, "milDay": day.day, "milType": "IS", "milVnos": code,
               "milCus": code, "milStk": "STK", "milPer": "SELLER", "milListno": 1, "mix_date": str(day),
               "milSum": 100.0, "mihCancel": 0, "mihStatus": 0}
        transactions.append(row)
        if invoice_sk is not None:
            facts.append({key: value for key, value in row.items() if key in fact_schema}
                         | {"InvoiceSK": invoice_sk, "FactInvoiceSK": invoice_sk})

    for sk, (company_sk, code, _) in enumerate(cases, 1):
        transaction(company_sk, code, sk)
    transaction(1, "NO_INVOICE", None)
    transaction(1, "MISSING_HEADER", 100)
    transaction(1, "LATE_SHOP", 101)

    for dataset in sorted({d for d, _ in tables} | {"function_dataset", "fact_view"}):
        api("datasets", {"datasetReference": {"projectId": PROJECT, "datasetId": dataset}, "location": "us-central1"})
    for (dataset, name), item in tables.items():
        api(f"datasets/{dataset}/tables", {"tableReference": {"projectId": PROJECT, "datasetId": dataset, "tableId": name},
                                          "schema": {"fields": [{"name": key, "type": kind}
                                                                for key, kind in item["schema"].items()]}})
        if item["rows"]:
            result = api(f"datasets/{dataset}/tables/{name}/insertAll", {"rows": [{"json": row} for row in item["rows"]]})
            assert not result.get("insertErrors"), result
    (args.evidence / "input-fixtures.json").write_text(json.dumps(
        {f"{d}.{n}": item for (d, n), item in tables.items()}, ensure_ascii=False, indent=2))

    project = scratch / "project"
    (project / "definitions").mkdir(parents=True)
    shutil.copytree(repo / "includes", project / "includes")
    cli = args.cli.absolute()
    (project / "node_modules").symlink_to(cli.parent.parent)
    shutil.copy(cli.parent.parent.parent / "package.json", project / "package.json")
    (project / "workflow_settings.yaml").write_text(
        f"defaultProject: {PROJECT}\ndefaultLocation: us-central1\ndefaultDataset: dataform\n"
        'defaultAssertionDataset: dataform_assertions\nvars:\n  RAW_BUCKET: "gs://unused"\n'
        '  MDS_BACKFILL_DAYS: "1"\n  BACKFILL_DAYS: "1"\n')
    sources = ["definitions/dimension/dim_customer_report_info.sqlx", "definitions/dimension/dim_customer_segment.sqlx",
               "definitions/view/dimension_view/view_dim_invoice.sqlx",
               "definitions/view/dimension_view/view_dim_customer_report_info.sqlx",
               "definitions/view/fact_view/view_fact_transcation.sqlx", "definitions/initial/create_all_function.sqlx"]
    for source in sources:
        shutil.copy(repo / source, project / "definitions" / Path(source).name)
    declarations = {(dataset, name) for dataset, name in tables}
    declarations.update(("dimension_table", name) for name in ("update_sk_sale_rep_group", "dim_group_customer", "dim_guarantee"))
    (project / "definitions/declarations.js").write_text("\n".join(
        f'declare({{database: "{PROJECT}", schema: "{dataset}", name: "{name}"}});'
        for dataset, name in sorted(declarations)))
    graph = json.loads(subprocess.check_output([str(cli), "compile", str(project), "--json"], text=True))
    (args.evidence / "compiled-actions.json").write_text(json.dumps(graph, indent=2))
    functions = next(action for action in graph["operations"] if action["target"]["name"] == "create_all_function")
    # The first functions and final clean_company_prefix are the real UDFs used by these actions.
    udf_sql = "\n".join(functions["queries"])
    for part in udf_sql.split("CREATE OR REPLACE FUNCTION")[1:]:
        identifier = part.split("`", 2)[1].rsplit(".", 1)[1]
        if identifier in ("fn_get_scg_customer_ids", "fn_flag_exc", "fn_flag_scg", "clean_company_prefix"):
            query("CREATE OR REPLACE FUNCTION" + part)
    env = dict(os.environ, BIGQUERY_EMULATOR_HOST=f"{endpoint}/bigquery/v2")
    for key in ("GOOGLE_APPLICATION_CREDENTIALS", "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE"):
        env.pop(key, None)
    credentials = project / ".df-credentials.json"
    credentials.write_text(json.dumps({"projectId": PROJECT, "location": "us-central1"}))

    def run(action):
        command = [str(cli), "run", str(project), "--actions", action, "--credentials", str(credentials)]
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=180)
        transcripts.append({"command": command, "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
        (args.evidence / "dataform-run.json").write_text(json.dumps(transcripts, indent=2))
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    def check(name, passed, detail):
        checks.append({"name": name, "passed": passed, "detail": detail})
        (args.evidence / "behavior-checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2))

    run("view_dim_invoice")
    invoice_rows = query(f"SELECT InvoiceSK, mihCus, CustomerReportName FROM `{PROJECT}.dimension_view.view_dim_invoice` ORDER BY InvoiceSK")
    check("the real invoice view leaves unusable names NULL", [r["CustomerReportName"] for r in invoice_rows]
          == ["Named Shop", None, None, None, None, "Named Shop"], invoice_rows)
    run("dim_customer_segment")
    run("dim_customer_report_info")
    before = query(f"SELECT * FROM `{PROJECT}.dimension_table.dim_customer_report_info` ORDER BY CustomerReportInfoSK")
    # New invoices may arrive between the dimension rebuild and the reporting query.
    late = {"CompanySK": 1, "companyID": "ag01", "InvoiceSK": 101, "mihType": "IS", "mihVnos": "LATE_SHOP",
            "mihCus": "LATE_SHOP", "mihCancel": 0, "mihStatus": 0, "mix_date": f"{day} 12:00:00"}
    result = api("datasets/dimension_table/tables/dim_invoice/insertAll", {"rows": [{"json": late}]})
    assert not result.get("insertErrors"), result
    result = api("datasets/dimension_view/tables/view_dim_customer/insertAll", {"rows": [{"json": {
        "CompanySK": 1, "companyID": "ag01", "debcode": "LATE_SHOP", "debnamet": "Late Shop", "FlagMDSNickName": False}}]})
    assert not result.get("insertErrors"), result
    run("view_dim_customer_report_info")
    sql = (f"SELECT f.InvoiceSK, f.milVnos, f.CompanySK, f.milSum, f.CustomerReportInfoSK, "
           "cri.CustomerReportName, cri.CustomerSegmentSK, seg.Segment3 "
           f"FROM `{PROJECT}.fact_view.view_fact_transcation` f "
           f"LEFT JOIN `{PROJECT}.dimension_view.view_dim_customer_report_info` cri USING (CustomerReportInfoSK) "
           f"LEFT JOIN `{PROJECT}.dimension_table.dim_customer_segment` seg USING (CustomerSegmentSK) "
           "ORDER BY f.CompanySK, f.milVnos")
    fact_source = "definitions/view/fact_view/view_fact_transcation.sqlx"
    local_fact_source = project / "definitions/view_fact_transcation.sqlx"
    local_fact_source.write_text(subprocess.check_output(["git", "show", f"{args.base}:{fact_source}"], cwd=repo, text=True))
    try:
        run("view_fact_transcation")
        base_rows = query(sql)
        (args.evidence / "reporting-output-before-change.json").write_text(json.dumps(base_rows, ensure_ascii=False, indent=2))
    finally:
        shutil.copy(repo / fact_source, local_fact_source)
    run("view_fact_transcation")
    rows = query(sql)
    (args.evidence / "reporting-output.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    actual = {row["milVnos"]: row for row in rows if row["milVnos"] is not None}
    base_actual = {row["milVnos"]: row for row in base_rows if row["milVnos"] is not None}
    check("the base fact view reproduces NULL mappings for real unmatched invoices",
          all(base_actual[code]["InvoiceSK"] is not None and base_actual[code]["CustomerReportInfoSK"] is None
              and actual.get(code, {}).get("CustomerReportInfoSK") == -1
              for code in ("PREFIX", "LIMITED", "NULL_NAME", "111020730.", "MISSING_HEADER", "LATE_SHOP")),
          {"before": base_rows, "after": rows})
    check("the mapping change preserves matched shops and non-invoice rows from the base fact view",
          all(actual.get(code) == base_actual[code] for code in ("NAMED", "NAMED_OTHER", "NO_INVOICE"))
          and [row for row in rows if row["milVnos"] is None] == [row for row in base_rows if row["milVnos"] is None],
          {"before": base_rows, "after": rows})
    check("all invoice and non-invoice transaction fixtures reach the reporting surface",
          len(actual) == len(transactions) and len(rows) == len(transactions) + 2, rows)
    for code in ("PREFIX", "LIMITED", "NULL_NAME", "111020730.", "MISSING_HEADER", "LATE_SHOP"):
        row = actual.get(code, {})
        check(f"unmatched invoice maps to blank Non-Segment SK -1: {code}",
              (row.get("CustomerReportInfoSK"), row.get("CustomerReportName"), row.get("CustomerSegmentSK"), row.get("Segment3"))
              == (-1, None, -1, "Non-Segment"), row)
    named = [actual.get(code, {}) for code in ("NAMED", "NAMED_OTHER")]
    check("matched names preserve distinct company-specific positive SKs",
          all(row.get("CustomerReportInfoSK", -1) > 0 and row.get("CustomerReportName") == "Named Shop" for row in named)
          and named[0].get("CustomerReportInfoSK") != named[1].get("CustomerReportInfoSK"), named)
    fillers = [row for row in rows if row["milVnos"] is None]
    check("calendar fillers stay zero-amount with NULL customer mapping",
          len(fillers) == 2 and all(row["milSum"] == 0 and row["InvoiceSK"] is None
                                   and row["CustomerReportInfoSK"] is None for row in fillers), fillers)
    check("a transaction without an invoice stays unmapped",
          actual.get("NO_INVOICE", {}).get("CustomerReportInfoSK") is None
          and actual.get("NO_INVOICE", {}).get("InvoiceSK") is None, actual.get("NO_INVOICE"))
    check("a spaced reserved-like GOLD MDS name cannot capture unmatched invoices",
          any(row["CustomerReportName"] == "ไม่ระบุชื่อ ลูกค้า" and row["CustomerReportInfoSK"] > 0
              and row["CustomerSegmentSK"] != -1 for row in before)
          and all(actual[code]["CustomerReportInfoSK"] == -1 for code in ("PREFIX", "LIMITED", "NULL_NAME", "111020730.")), before)
    run("dim_customer_report_info")
    after = query(f"SELECT * FROM `{PROJECT}.dimension_table.dim_customer_report_info` ORDER BY CustomerReportInfoSK")
    check("a dimension rebuild retains exactly one reserved member",
          len([row for row in after if row["CustomerReportInfoSK"] == -1]) == 1, after)
    rebuilt = query(sql)
    check("a newly known shop resolves from -1 to its positive customer SK after rebuild",
          next(row for row in rebuilt if row["milVnos"] == "LATE_SHOP")["CustomerReportInfoSK"] > 0, rebuilt)
    (args.evidence / "reporting-output-after-rebuild.json").write_text(json.dumps(rebuilt, ensure_ascii=False, indent=2))
    failures = [item["name"] for item in checks if not item["passed"]]
    print(json.dumps({"failures": failures, "fixture_date": str(today), "reporting_rows": len(rows),
                      "evidence": str(args.evidence)}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

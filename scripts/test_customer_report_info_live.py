#!/usr/bin/env python3
"""Run the real Dataform action against an explicitly supplied local BigQuery server.

No ADC or production endpoint is used. The fixtures are the action's input tables,
not a Python reimplementation of the transformation. Requires Dataform CLI 3.0.0.
The server must refresh table metadata after a schema-changing CREATE OR REPLACE.
"""

import argparse
import atexit
import datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import urllib.error
import urllib.parse
import urllib.request


PROJECT = "nm-local-cri"
ACTION = "dim_customer_report_info"
SOURCE = f"definitions/dimension/{ACTION}.sqlx"
BASE = "c9b7089aa5c3e8209c4f98d406fbfa6f36c7ef12"
BEFORE_FIX = "4bfa8aa"
REMOVED_BASE = "f783450054355cf07bdaf956a94b406089353837"
NARROWED_TRACE = "81e9d7819477e2700752975f07912b22b5020746"


def compatibility_transport(upstream, evidence):
    """Normalize equivalent UDF identifier quoting for bigquery-emulator 0.8.1.

    Its catalog cannot resolve the full dotted path inside one pair of backticks.
    This adapter changes identifier quoting only, never the transformation or UDF
    body, and records every normalized request for review.
    """
    quoted = f"`{PROJECT}.function_dataset.clean_company_prefix`"
    segmented = f"`{PROJECT}`.function_dataset.clean_company_prefix"
    log = evidence / "udf-compatibility-requests.jsonl"

    class Proxy(BaseHTTPRequestHandler):
        def forward(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            if body:
                payload = json.loads(body)
                holder = payload if "query" in payload else payload.get("configuration", {}).get("query", {})
                sql = holder.get("query")
                if isinstance(sql, str) and quoted in sql:
                    normalized = sql.replace(quoted, segmented)
                    with log.open("a") as output:
                        output.write(json.dumps({"path": self.path, "original": sql, "normalized": normalized},
                                                ensure_ascii=False) + "\n")
                    holder["query"] = normalized
                    body = json.dumps(payload).encode()
            req = urllib.request.Request(upstream + self.path, data=body or None, method=self.command,
                                         headers={"Content-Type": "application/json"})
            try:
                response = urllib.request.urlopen(req, timeout=120)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                content = response.read()
                self.send_response(response.code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

        do_GET = do_POST = do_PATCH = do_DELETE = do_PUT = forward

        def log_message(self, *unused):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Proxy)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def close():
        server.shutdown()
        server.server_close()
        thread.join()

    atexit.register(close)
    return f"http://127.0.0.1:{server.server_port}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--quoted-udf-workaround", action="store_true",
                        help="normalize equivalent UDF identifier quoting for bigquery-emulator 0.8.1")
    args = parser.parse_args()
    endpoint = args.endpoint.rstrip("/")
    if urllib.parse.urlparse(endpoint).hostname not in ("127.0.0.1", "localhost"):
        parser.error("only a disposable loopback BigQuery server is allowed")
    repo = Path(__file__).resolve().parents[1]
    scratch = args.scratch.resolve()
    if not scratch.is_relative_to(repo):
        parser.error("scratch directory must be inside the worktree")
    scratch.mkdir(parents=True, exist_ok=True)
    args.evidence.mkdir(parents=True, exist_ok=True)
    if args.quoted_udf_workaround:
        endpoint = compatibility_transport(endpoint, args.evidence)
    cli = args.cli.absolute()
    transcripts = []
    responses = []

    def api(path, body=None):
        req = urllib.request.Request(
            f"{endpoint}/bigquery/v2/projects/{PROJECT}/{path}",
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(error.read().decode()) from error

    def query(sql):
        response = api("queries", {"query": sql, "useLegacySql": False})
        responses.append({"query": sql, "response": response})
        if response.get("errors"):
            raise RuntimeError(response["errors"])
        assert response.get("jobComplete"), response
        fields = response.get("schema", {}).get("fields", [])
        rows = []
        for row in response.get("rows", []):
            decoded = {}
            for field, value in zip(fields, row["f"]):
                value = value.get("v")
                if value is not None and field["type"] in ("INTEGER", "INT64"):
                    value = int(value)
                elif value is not None and field["type"] in ("FLOAT", "FLOAT64"):
                    value = float(value)
                elif value is not None and field["type"] in ("BOOLEAN", "BOOL"):
                    value = value in (True, "true")
                decoded[field["name"]] = value
            rows.append(decoded)
        return rows, fields

    today = dt.date.fromisoformat(query("SELECT CURRENT_DATE('Asia/Bangkok') AS today")[0][0]["today"])
    past = str(today - dt.timedelta(days=365))
    yesterday = str(today - dt.timedelta(days=1))
    tomorrow = str(today + dt.timedelta(days=1))
    future = str(today + dt.timedelta(days=365))
    last_month = str(today.replace(day=1) - dt.timedelta(days=1))
    tables = {}

    def table(dataset, name, fields):
        tables[(dataset, name)] = (fields, [])
        return tables[(dataset, name)][1]

    companies = table("dimension_table", "dim_company", {"CompanySK": "INTEGER", "companyID": "STRING"})
    companies.extend([{"CompanySK": 1, "companyID": "ag01"}, {"CompanySK": 2, "companyID": "aa05"}])
    departments = table("dimension_table", "dim_department_last", {
        "CompanySK": "INTEGER", "DepartmentSK": "INTEGER", "DepartmentID": "STRING",
        "StartDate": "DATE", "EndDate": "DATE", "SectionSK": "INTEGER",
        "RegionSK": "INTEGER", "DirectorSK": "INTEGER",
    })
    for company_sk in (1, 2):
        for sk, dep_id, end in ((1, "TA_A", future), (2, "TA_B", future), (3, "TA_MDS", future),
                                (4, "TA_EXPIRED", yesterday), (5, "DummyTA", future),
                                (6, "TA_TODAY", str(today)), (7, "TA_NULLDATE", None)):
            departments.append({"CompanySK": company_sk, "DepartmentSK": company_sk * 100 + sk,
                                "DepartmentID": dep_id, "StartDate": past, "EndDate": end,
                                "SectionSK": 10, "RegionSK": 20, "DirectorSK": 30})
    reps = table("dimension_table", "dim_sale_representative_last", {
        "companyID": "STRING", "CompanySK": "INTEGER", "EmployeeID": "STRING",
        "DepartmentSK": "INTEGER", "DepartmentID": "STRING", "CostChannelID": "STRING",
        "DepCode": "STRING", "StartDate": "DATE", "EndDate": "DATE",
    })

    def rep(employee, dep=1, *, company="ag01", start=past, end=future, cost=None, code=None, dep_id=None):
        company_sk = 1 if company == "ag01" else 2
        rep_dep = next((d["DepartmentID"] for d in departments
                        if d["CompanySK"] == company_sk and d["DepartmentSK"] == company_sk * 100 + dep), None)
        reps.append({"companyID": company, "CompanySK": company_sk, "EmployeeID": employee,
                     "DepartmentSK": company_sk * 100 + dep, "DepartmentID": dep_id or rep_dep,
                     "StartDate": start, "EndDate": end, "CostChannelID": cost, "DepCode": code})

    rep("REP_A")
    rep("REP_B", 2)
    rep("CHAIN_COST", cost="HOME_PRO")
    rep("CHAIN_CODE", code="THAI_WATSADU")
    rep("CHAIN_EXPIRED", 1, cost="HOME_PRO")
    rep("CHAIN_EXPIRED", 2, code="THAI_WATSADU", end=yesterday)
    rep("CHAIN_DANGLING")
    rep("CHAIN_DANGLING", 99, end=yesterday, code="EXPIRED_CHAIN", dep_id="TA_NOT_IN_MASTER")
    rep("CHAIN_FUTURE")
    rep("CHAIN_FUTURE", 2, start=tomorrow, cost="FUTURE_CHAIN")
    rep("PLAIN_MOVED", 2)
    rep("PLAIN_MOVED", 1, end=yesterday)
    rep("PLAIN_MULTI", 1)
    rep("PLAIN_MULTI", 2)
    rep("DUMMY_HISTORY")
    rep("DUMMY_HISTORY", 5, code="IGNORED_DUMMY")
    rep("NULL_DEPARTMENT_HISTORY")
    rep("NULL_DEPARTMENT_HISTORY", 99, code="IGNORED_NULL")
    rep("DEPARTMENT_EXPIRED", 4)
    rep("DUMMY_ONLY", 5)
    rep("REP_EXPIRED", end=yesterday)
    rep("REP_FUTURE", start=tomorrow)
    rep("BOUNDARY_TODAY", 6, start=str(today), end=str(today))
    rep("NULL_DATES", 7, start=None, end=None)
    rep("REUSED_EMPLOYEE", 1, company="ag01")
    rep("REUSED_EMPLOYEE", 2, company="aa05", cost="CHAIN_OTHER_COMPANY")
    invoice = table("dimension_view", "view_dim_invoice", {
        "companyID": "STRING", "CustomerReportName": "STRING", "mihCus": "STRING",
        "mix_date": "DATETIME", "mihVnos": "STRING",
    })
    customers = table("dimension_view", "view_dim_customer", {
        "companyID": "STRING", "debcode": "STRING", "debnamet": "STRING",
        "FlagMDSNickName": "BOOLEAN", "NicknameCustomer": "STRING",
    })
    debs = table("validated_mac5", "deb", {
        "company_id": "STRING", "debcode": "STRING", "debsalesp": "STRING", "debdate": "DATETIME",
    })
    quotes = table("validated_mac5", "tbook_quotation", {
        "company_id": "STRING", "agent1": "STRING", "channel": "STRING", "dinsert": "DATETIME", "id": "STRING",
    })
    masters = table("mds_dataset", "mds_data_customer_report_master", {
        "companyID": "STRING", "CustomerReportName": "STRING", "DepartmentID": "STRING",
        "CustomerTier": "STRING", "FlagPC": "BOOLEAN", "ShopOnline": "STRING", "OnlinePercent": "STRING",
        "id": "STRING", "is_active": "BOOLEAN", "updated_at": "TIMESTAMP",
    })
    segments = table("dimension_table", "dim_customer_segment", {
        "CompanySK": "INTEGER", "CustomerSegmentSK": "INTEGER", "Segment3": "STRING",
    })
    for company_sk in (1, 2):
        for sk, name in enumerate(("DC", "DA", "GOLD", "BRONZE", "SILVER"), 1):
            segments.append({"CompanySK": company_sk, "CustomerSegmentSK": company_sk * 1000 + sk, "Segment3": name})
    expected = {}

    def shop(name, employee="REP_A", *, company="ag01", code=None, own=None, date=None,
             vnos="V001", nickname=None, channel="DC", debdate=None, ta="TA_A", source="DEBSALESP"):
        code = code or "".join(name.split())
        date = date or f"{today} 10:00:00"
        invoice.append({"companyID": company, "CustomerReportName": name, "mihCus": code,
                        "mix_date": date, "mihVnos": vnos})
        if not any(c["companyID"] == company and c["debcode"] == code for c in customers):
            customers.append({"companyID": company, "debcode": code, "debnamet": own or name,
                              "FlagMDSNickName": nickname is not None, "NicknameCustomer": nickname})
            debs.append({"company_id": company, "debcode": code, "debsalesp": employee,
                         "debdate": debdate or f"{today} 00:00:00"})
            if channel is not None:
                quotes.append({"company_id": company, "agent1": code + " customer", "channel": channel,
                               "dinsert": f"{today} 00:00:00", "id": str(len(quotes) + 1)})
        expected[(company, "".join(name.split()))] = {"DepartmentID": ta, "TASource": source}

    def mds(name, department, *, tier="GOLD", active=True, updated=None, ident=None):
        masters.append({"companyID": "ag01", "CustomerReportName": name, "DepartmentID": department,
                        "CustomerTier": tier, "FlagPC": True, "ShopOnline": "Online shop",
                        "OnlinePercent": "25.5", "id": ident or name, "is_active": active,
                        "updated_at": updated or f"{today}T00:00:00Z"})

    shop("ชื่อ XX", code="A4566666", date=f"{yesterday} 10:00:00")
    shop("ชื่อ XX", "REP_B", code="A05699", own="ชื่อ XY", channel="DA")
    expected[("ag01", "ชื่อXX")].update(DepartmentID="TA_A")
    shop("Latest Matching", code="OLDER", date=f"{yesterday} 10:00:00")
    shop("Latest Matching", "REP_B", code="NEWER", ta="TA_B")
    shop("Tie Matching", code="TIE_A", vnos="V001")
    shop("Tie Matching", "REP_B", code="TIE_B", vnos="V002", ta="TA_B")
    shop("Latest Unusable", code="USABLE_OLDER", date=f"{yesterday} 10:00:00")
    shop("Latest Unusable", "CHAIN_COST", code="CHAIN_LATEST", ta=None, source=None)
    shop("Whitespace Name", own="Whitespace\tName", nickname="Whitespace\tName")
    shop("Nickname Wins", own="Different legal name", nickname="Nickname Wins")
    shop("ชื่อไทย", own="บริษัท ชื่อไทย จำกัด")
    shop("MDS Priority", "REP_B", ta="TA_MDS", source="MDS")
    mds("MDS Priority", " TA_MDS\t")
    shop("MDS Chain Priority", "CHAIN_EXPIRED", ta="TA_MDS", source="MDS")
    mds("MDS Chain Priority", "TA_MDS")
    shop("Invalid MDS Fallback")
    mds("Invalid MDS Fallback", "TA_NOT_FOUND")
    shop("Inactive MDS")
    mds("Inactive MDS", "TA_MDS", active=False)
    mds("MDS Only", "TA_MDS")
    expected[("ag01", "MDSOnly")] = dict(DepartmentID="TA_MDS", TASource="MDS")
    for name, employee in (("Single Cost Chain", "CHAIN_COST"), ("Single Depcode Chain", "CHAIN_CODE"),
                           ("Expired Chain", "CHAIN_EXPIRED"), ("Dangling Expired Chain", "CHAIN_DANGLING"),
                           ("Future Chain", "CHAIN_FUTURE")):
        shop(name, employee, ta=None, source=None)
    shop("Plain Moved", "PLAIN_MOVED", ta="TA_B")
    shop("Plain Multiple", "PLAIN_MULTI", ta=None, source=None)
    shop("Dummy History", "DUMMY_HISTORY")
    shop("Null Department History", "NULL_DEPARTMENT_HISTORY")
    shop("Today Inclusive", "BOUNDARY_TODAY", ta="TA_TODAY")
    shop("Null Dates", "NULL_DATES", ta="TA_NULLDATE")
    for name, employee in (("Expired Department", "DEPARTMENT_EXPIRED"), ("Dummy Only", "DUMMY_ONLY"),
                           ("Expired Rep", "REP_EXPIRED"), ("Future Rep", "REP_FUTURE"),
                           ("Missing Rep", "NO_SUCH_REP"), ("No Debsalesp", None)):
        shop(name, employee, ta=None, source=None)
    expected[("ag01", "NoDebsalesp")].update(TADebcode="NoDebsalesp")
    for name in ("SCG Branch", "CRC Branch", "Mec Branch"):
        shop(name, own="Different customer name", ta=None, source=None)
    shop("Missing Deb", ta=None, source=None)
    debs[:] = [d for d in debs if d["debcode"] != "MissingDeb"]
    shop("Company Boundary", "REUSED_EMPLOYEE", code="SHARED_CODE")
    shop("Company Boundary", "REUSED_EMPLOYEE", code="SHARED_CODE", company="aa05", ta=None, source=None)
    shop("TT Current Month", channel="TT")
    shop("TT Previous Month", channel="TT", debdate=f"{last_month} 00:00:00")
    shop("Unknown Tier", channel="DA")
    mds("Unknown Tier", "", tier="UNKNOWN")
    shop("No Channel", channel=None)
    shop("Channel Guard", channel="DA")
    quotes.append({"company_id": "ag01", "agent1": "ChannelGuard customer", "channel": "INVALID",
                   "dinsert": f"{tomorrow} 00:00:00", "id": "999"})
    shop("Dup Name", code="DUP1")
    shop("Dup  Name", code="DUP2", own="Dup Name", date=f"{yesterday} 10:00:00")
    mds("Dup Name", "TA_B", tier="GOLD", updated=f"{yesterday}T00:00:00Z", ident="OLD_MASTER")
    mds("Dup  Name", "TA_MDS", tier="GOLD", ident="NEW_MASTER")
    expected[("ag01", "DupName")].update(DepartmentID="TA_MDS", TASource="MDS")
    invoice.append({"companyID": "ag01", "CustomerReportName": "   ", "mihCus": "BLANK",
                    "mix_date": f"{today} 00:00:00", "mihVnos": "BLANK"})

    for dataset in sorted({d for d, _ in tables} | {"function_dataset"}):
        api("datasets", {"datasetReference": {"projectId": PROJECT, "datasetId": dataset}, "location": "us-central1"})
    for (dataset, name), (fields, rows) in tables.items():
        api(f"datasets/{dataset}/tables", {"tableReference": {"projectId": PROJECT, "datasetId": dataset, "tableId": name},
            "schema": {"fields": [{"name": n, "type": t} for n, t in fields.items()]}})
        if rows:
            result = api(f"datasets/{dataset}/tables/{name}/insertAll", {"rows": [{"json": row} for row in rows]})
            assert not result.get("insertErrors"), result
    (args.evidence / "input-fixtures.json").write_text(json.dumps(
        {f"{d}.{n}": {"schema": fields, "rows": rows} for (d, n), (fields, rows) in tables.items()}, ensure_ascii=False, indent=2))

    def compile_action(label, ref=None):
        project = scratch / label
        (project / "definitions").mkdir(parents=True)
        shutil.copytree(repo / "includes", project / "includes")
        (project / "node_modules").symlink_to(cli.parent.parent)
        shutil.copy(cli.parent.parent.parent / "package.json", project / "package.json")
        (project / "workflow_settings.yaml").write_text(
            f"defaultProject: {PROJECT}\ndefaultLocation: us-central1\ndefaultDataset: dataform\n"
            'defaultAssertionDataset: dataform_assertions\nvars:\n  RAW_BUCKET: "gs://unused"\n'
            '  MDS_BACKFILL_DAYS: "1"\n  BACKFILL_DAYS: "1"\n')
        source = (repo / SOURCE).read_text() if ref is None else subprocess.check_output(
            ["git", "show", f"{ref}:{SOURCE}"], cwd=repo, text=True)
        (project / "definitions" / f"{ACTION}.sqlx").write_text(source)
        shutil.copy(repo / "definitions/initial/create_all_function.sqlx", project / "definitions/create_all_function.sqlx")
        declared = {"dim_company", "dim_department_last", "update_sk_sale_rep_group", "dim_customer_segment",
                    "dim_sale_representative_last", "dim_invoice", "dim_aging", "dim_order", "dim_customer", "dim_group_customer"}
        declarations = [f'declare({{database: "{PROJECT}", schema: "dimension_table", name: "{name}"}});' for name in sorted(declared)]
        declarations += [f'declare({{database: "{PROJECT}", schema: "validated_mac5", name: "{name}"}});'
                         for name in ("deb", "tbook_quotation", "mec")]
        (project / "definitions/declarations.js").write_text("\n".join(declarations))
        result = subprocess.run([str(cli), "compile", str(project), "--json"], capture_output=True, text=True, check=True)
        graph = json.loads(result.stdout)
        target = next(t for t in graph["tables"] if t["target"]["name"] == ACTION)
        (args.evidence / f"{label}-compiled.sql").write_text(target["query"])
        return project, graph, target["query"]

    base_project, _, _ = compile_action("base", BASE)
    _, _, before_sql = compile_action("before-r2", BEFORE_FIX)
    removed_project, _, _ = compile_action("removed-base", REMOVED_BASE)
    _, _, narrowed_sql = compile_action("narrowed-trace", NARROWED_TRACE)
    project, graph, target_sql = compile_action("target")
    functions = next(o for o in graph["operations"] if o["target"]["name"] == "create_all_function")
    # Execute the compiler-emitted final SQL UDF, clean_company_prefix.
    udf_sql = "CREATE OR REPLACE FUNCTION" + "\n".join(functions["queries"]).rsplit("CREATE OR REPLACE FUNCTION", 1)[1]
    query(udf_sql)
    before_rows, _ = query(before_sql)
    narrowed_rows, _ = query(narrowed_sql)
    env = dict(os.environ, BIGQUERY_EMULATOR_HOST=f"{endpoint}/bigquery/v2")
    # A custom endpoint makes the official BigQuery client omit authentication.
    for key in ("GOOGLE_APPLICATION_CREDENTIALS", "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE"):
        env.pop(key, None)

    def run_action(action_project):
        credentials = action_project / ".df-credentials.json"
        credentials.write_text(json.dumps({"projectId": PROJECT, "location": "us-central1"}))
        command = [str(cli), "run", str(action_project), "--actions", ACTION, "--credentials", str(credentials)]
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=180)
        transcripts.append({"command": command, "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
        (args.evidence / "dataform-run.json").write_text(json.dumps(transcripts, indent=2))
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)

    # Rebuild an existing table, rather than checking only a fresh SELECT schema.
    run_action(base_project)
    base_rows, base_fields = query(f"SELECT * FROM `{PROJECT}.dimension_table.{ACTION}` ORDER BY CustomerReportInfoSK")
    (args.evidence / "base-schema.json").write_text(json.dumps(base_fields, indent=2))
    run_action(removed_project)
    removed_rows, removed_fields = query(f"SELECT * FROM `{PROJECT}.dimension_table.{ACTION}` ORDER BY CustomerReportInfoSK")
    (args.evidence / "removed-base-schema.json").write_text(json.dumps(removed_fields, indent=2))
    (args.evidence / "removed-base-rows.json").write_text(json.dumps(removed_rows, ensure_ascii=False, indent=2))
    run_action(project)
    actual_rows, fields = query(f"SELECT * FROM `{PROJECT}.dimension_table.{ACTION}` ORDER BY CustomerReportInfoSK")

    def index(rows):
        return {(r["CompanyID"], "".join(r["CustomerReportName"].split())): r for r in rows}

    actual = index(actual_rows)
    before = index(before_rows)
    base = index(base_rows)
    removed = index(removed_rows)
    narrowed = index(narrowed_rows)
    (args.evidence / "materialized-target-rows.json").write_text(json.dumps(actual_rows, ensure_ascii=False, indent=2))
    (args.evidence / "base-rows.json").write_text(json.dumps(base_rows, ensure_ascii=False, indent=2))
    (args.evidence / "before-r2-rows.json").write_text(json.dumps(before_rows, ensure_ascii=False, indent=2))
    (args.evidence / "narrowed-trace-rows.json").write_text(json.dumps(narrowed_rows, ensure_ascii=False, indent=2))
    (args.evidence / "target-schema.json").write_text(json.dumps(fields, indent=2))
    failures = []
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(name)

    check("output has exactly one row per company and whitespace-normalized name",
          len(actual_rows) == len(actual) == len(expected) and actual.keys() == expected.keys(),
          {"rows": len(actual_rows), "expected": len(expected)})
    for key, values in expected.items():
        observed = {k: actual.get(key, {}).get(k) for k in values}
        check(f"TA selection: {key[0]} / {key[1]}", observed == values, {"expected": values, "actual": observed})
    stable_columns = ("CustomerReportInfoSK", "CompanySK", "CustomerSegmentSK", "CompanyID", "CustomerReportName",
                      "FlagPC", "ShopOnline", "OnlinePercent", "SegmentSource", "SegmentDebcode", "SegmentChannel", "MdsID")
    retained_columns = stable_columns + ("DepartmentID", "TASource", "TADebcode")
    stable = actual.keys() == base.keys() and all(
        {k: r[k] for k in retained_columns} == {k: actual[key][k] for k in retained_columns}
        for key, r in base.items())
    check("every retained value, including TA lookup code, equals base output",
          stable, {"columns": retained_columns})
    for name, segment, source in (("ชื่อ XX", 1002, "CHANNEL"), ("SCG Branch", 1001, "CHANNEL"),
                                  ("TT Current Month", 1004, "CHANNEL"), ("TT Previous Month", 1005, "CHANNEL"),
                                  ("Unknown Tier", 1001, "DEFAULT"), ("No Channel", 1001, "DEFAULT"),
                                  ("Channel Guard", 1002, "CHANNEL"), ("MDS Priority", 1003, "MDS")):
        row = actual[("ag01", "".join(name.split()))]
        check(f"segment contract: {name}", (row["CustomerSegmentSK"], row["SegmentSource"]) == (segment, source), row)
    expected_schema = list(stable_columns) + ["DepartmentID", "TASource", "TADebcode"]
    removed_columns = ("TAEmployeeID",)
    check("TADebcode is NULL when MDS supplies the TA",
          all(r["TADebcode"] is None for r in actual_rows if r["TASource"] == "MDS"), actual_rows)
    check("TADebcode keeps the customer code that supplied the TA",
          actual[("ag01", "ชื่อXX")]["TADebcode"] == "A4566666", actual[("ag01", "ชื่อXX")])
    for name in ("NoDebsalesp", "MissingRep", "MissingDeb", "PlainMultiple", "SingleCostChain",
                 "ExpiredDepartment", "DummyOnly", "ExpiredRep", "FutureRep", "LatestUnusable"):
        row = actual[("ag01", name)]
        code = "CHAIN_LATEST" if name == "LatestUnusable" else name
        check(f"diagnostic customer code survives unresolved TA: {name}",
              row["DepartmentID"] is None and row["TASource"] is None and row["TADebcode"] == code, row)
    for name in ("SCGBranch", "CRCBranch", "MecBranch"):
        check(f"a mismatched customer name cannot supply a TA lookup code: {name}",
              actual[("ag01", name)]["TADebcode"] is None, actual[("ag01", name)])
    check("diagnostic-code regression reproduced before review fix and corrected",
          narrowed[("ag01", "NoDebsalesp")]["TADebcode"] is None
          and actual[("ag01", "NoDebsalesp")]["TADebcode"] == "NoDebsalesp",
          {"before": narrowed[("ag01", "NoDebsalesp")], "after": actual[("ag01", "NoDebsalesp")]})
    check("immediate base table omits both TA trace columns",
          [f["name"] for f in removed_fields] == list(stable_columns) + ["DepartmentID", "TASource"], removed_fields)
    check("rebuilding the immediate base restores only the TADebcode column",
          fields == removed_fields + [{"name": "TADebcode", "type": "STRING", "mode": "NULLABLE"}], fields)
    check("all existing values equal the immediate base output after restoration",
          removed.keys() == actual.keys() and all(
              {k: actual[key][k] for k in row} == row for key, row in removed.items()),
          {"columns": [f["name"] for f in removed_fields]})
    check("base materialized table reproduces exposed employee and TA customer codes",
          all(c in {f["name"] for f in base_fields} for c in ("TAEmployeeID", "TADebcode"))
          and any(all(row[c] is not None for c in ("TAEmployeeID", "TADebcode")) for row in base_rows), base_fields)
    check("rebuilding the existing table removes TAEmployeeID and keeps TADebcode in its schema",
          [f["name"] for f in fields] == expected_schema, fields)
    check("all retained column types equal the base materialized schema",
          fields == [f for f in base_fields if f["name"] not in removed_columns], fields)
    metadata = api(f"datasets/dimension_table/tables/{ACTION}")
    (args.evidence / "target-table-metadata.json").write_text(json.dumps(metadata, indent=2))
    check("table metadata also exposes exactly the retained columns",
          [f["name"] for f in metadata["schema"]["fields"]] == expected_schema, metadata["schema"])
    rejected = []
    for column in removed_columns:
        sql = f"SELECT {column} FROM `{PROJECT}.dimension_table.{ACTION}`"
        try:
            query(sql)
        except RuntimeError as error:
            rejected.append({"query": sql, "error": str(error)})
            missing_column = any(f"{phrase}{column}".lower() in str(error).lower()
                                 for phrase in ("Unrecognized name: ", "Column not found: ", "no such column: "))
            check(f"consumers cannot select removed column {column}", missing_column, str(error))
        else:
            check(f"consumers cannot select removed column {column}", False, "query unexpectedly succeeded")
    (args.evidence / "removed-column-query-errors.json").write_text(json.dumps(rejected, indent=2))
    run_action(project)
    rerun_rows, rerun_fields = query(f"SELECT * FROM `{PROJECT}.dimension_table.{ACTION}` ORDER BY CustomerReportInfoSK")
    check("a second rebuild keeps the removed columns absent and all retained values unchanged",
          rerun_fields == fields and rerun_rows == actual_rows, {"schema": rerun_fields, "rows": len(rerun_rows)})
    for key in (("ag01", "SingleCostChain"), ("ag01", "SingleDepcodeChain"),
                ("ag01", "ExpiredChain"), ("ag01", "DanglingExpiredChain"), ("ag01", "FutureChain")):
        check(f"R2 regression reproduced before fix and corrected: {key[1]}",
              before[key]["DepartmentID"] is not None and actual[key]["DepartmentID"] is None,
              {"before": before[key], "after": actual[key]})
    check("MDS fields pass through with their public types",
          actual[("ag01", "MDSPriority")]["FlagPC"] is True
          and actual[("ag01", "MDSPriority")]["OnlinePercent"] == 25.5
          and actual[("ag01", "MDSPriority")]["ShopOnline"] == "Online shop",
          actual[("ag01", "MDSPriority")])
    (args.evidence / "behavior-checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2))
    (args.evidence / "query-responses.json").write_text(json.dumps(responses, ensure_ascii=False, indent=2))
    print(json.dumps({"failures": failures, "fixture_date": str(today), "materialized_rows": len(actual_rows),
                      "evidence": str(args.evidence)}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

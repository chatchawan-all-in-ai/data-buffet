#!/usr/bin/env python3
"""Run the real Dataform table and view against a supplied local BigQuery server.

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
VIEW_ACTION = f"view_{ACTION}"
VIEW_SOURCE = f"definitions/view/dimension_view/{VIEW_ACTION}.sqlx"
BASE = "c9b7089aa5c3e8209c4f98d406fbfa6f36c7ef12"
BEFORE_FIX = "4bfa8aa"
REMOVED_BASE = "f783450054355cf07bdaf956a94b406089353837"
NARROWED_TRACE = "81e9d7819477e2700752975f07912b22b5020746"
EMPLOYEE_BEFORE_FIX = "d183fbafbb942ac7e65bfd03792f7f5c41f378cb"
ACCEPTANCE_BASE = "a694ce5608ecc02ad74ebb9702087d1b7648e7d8"
MDT_BEFORE_CHANGE = "106973d5b5ce374a18a36eddefd31ad19ca07b1c"


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
        "DepartmentName": "STRING",
        "StartDate": "DATE", "EndDate": "DATE", "SectionSK": "INTEGER",
        "RegionSK": "INTEGER", "DirectorSK": "INTEGER", "SectionManagerSK": "INTEGER", "RegionManagerSK": "INTEGER",
    })
    for company_sk in (1, 2):
        for sk, dep_id, end in ((1, "TA_A", future), (2, "TA_B", future), (3, "TA_MDS", future),
                                (4, "TA_EXPIRED", yesterday), (5, "DummyTA", future),
                                (6, "TA_TODAY", str(today)), (7, "TA_NULLDATE", None),
                                (8, "HP_BK1_TA01", future), (9, "HP_S01_TA01", future),
                                (10, "HP_S02_TA01", future), (11, "TW_E01_TA01", future),
                                (12, "BT_BK1_TA01", future), (13, "GB_BK1_TA01", future),
                                (14, "MH_BK1_TA01", future), (15, "DH_BK1_TA01", future),
                                (16, "HP_EXPIRED_TA01", yesterday), (17, "HPX_BK1_TA01", future),
                                (18, "hp_lower_TA01", future)):
            departments.append({"CompanySK": company_sk, "DepartmentSK": company_sk * 100 + sk,
                                "DepartmentID": dep_id, "StartDate": past, "EndDate": end,
                                "DepartmentName": dep_id + " name",
                                "SectionSK": 10, "RegionSK": 20, "DirectorSK": 30,
                                "SectionManagerSK": 40, "RegionManagerSK": 50})
    table("dimension_table", "dim_section_last", {
        "SectionSK": "INTEGER", "SectionID": "STRING", "SectionName": "STRING",
    }).append({"SectionSK": 10, "SectionID": "SECTION", "SectionName": "Section name"})
    table("dimension_table", "dim_region_last", {
        "RegionSK": "INTEGER", "RegionID": "STRING", "RegionName": "STRING",
    }).append({"RegionSK": 20, "RegionID": "REGION", "RegionName": "Region name"})
    table("dimension_table", "dim_section_manager_last", {
        "SectionManagerSK": "INTEGER", "SectionManagerEmployeeID": "STRING", "SectionManagerName": "STRING",
        "SectionManagerSurname": "STRING", "SectionManagerNickname": "STRING",
    }).append({"SectionManagerSK": 40, "SectionManagerEmployeeID": "SM", "SectionManagerName": "Section",
               "SectionManagerSurname": "Manager", "SectionManagerNickname": None})
    table("dimension_table", "dim_region_manager_last", {
        "RegionManagerSK": "INTEGER", "RegionManagerEmployeeID": "STRING", "RegionManagerName": "STRING",
        "RegionManagerSurname": "STRING", "RegionManagerNickname": "STRING",
    }).append({"RegionManagerSK": 50, "RegionManagerEmployeeID": "RM", "RegionManagerName": "Region",
               "RegionManagerSurname": "Manager", "RegionManagerNickname": "Boss"})
    table("dimension_table", "dim_director_last", {
        "DirectorSK": "INTEGER", "DirectorID": "STRING", "DirectorName": "STRING",
    }).append({"DirectorSK": 30, "DirectorID": "DIRECTOR", "DirectorName": "Director name"})
    reps = table("dimension_table", "dim_sale_representative_last", {
        "SaleRepSK": "INTEGER", "companyID": "STRING", "CompanySK": "INTEGER", "EmployeeID": "STRING",
        "DepartmentSK": "INTEGER", "DepartmentID": "STRING", "CostChannelID": "STRING",
        "DepCode": "STRING", "StartDate": "DATE", "EndDate": "DATE",
        "EmployeeName": "STRING", "EmployeeSurname": "STRING", "EmployeeNickname": "STRING",
    })

    def rep(employee, dep=1, *, company="ag01", start=past, end=future, cost=None, code=None, dep_id=None):
        company_sk = 1 if company == "ag01" else 2
        rep_dep = next((d["DepartmentID"] for d in departments
                        if d["CompanySK"] == company_sk and d["DepartmentSK"] == company_sk * 100 + dep), None)
        reps.append({"SaleRepSK": len(reps) + 1, "companyID": company, "CompanySK": company_sk, "EmployeeID": employee,
                     "DepartmentSK": company_sk * 100 + dep, "DepartmentID": dep_id or rep_dep,
                     "StartDate": start, "EndDate": end, "CostChannelID": cost, "DepCode": code})

    def person(employee, name, surname, nickname=None, *, company="ag01"):
        # Name-only employee row from validated_mac5.per (no department).
        reps.append({"SaleRepSK": len(reps) + 1, "companyID": company, "CompanySK": 1 if company == "ag01" else 2,
                     "EmployeeID": employee,
                     "DepartmentSK": None, "DepartmentID": None, "StartDate": None, "EndDate": None,
                     "CostChannelID": None, "DepCode": None, "EmployeeName": name,
                     "EmployeeSurname": surname, "EmployeeNickname": nickname})

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
    rep("NAMED_DEPARTMENT", 2, cost="NAMED_CHAIN")
    reps[-1].update(EmployeeName="Named", EmployeeSurname="Department", EmployeeNickname="ND")
    # MDT (chain-store) employees: TA picked from the shop's deb.debgroup chain.
    rep("MDT_ONE", 8, cost="COST_HP")
    rep("MDT_ONE", 11, cost="COST_TW", end=yesterday)
    rep("MDT_SPLIT", 9, code="HP_S1")
    rep("MDT_SPLIT", 10, code="HP_S2")
    for dep in (8, 11, 12, 13, 14, 15):
        rep("MDT_ALL_CHAINS", dep, cost="CHAIN")
    rep("MDT_FILTERED", 8)
    rep("MDT_FILTERED", 9, end=yesterday, code="EXPIRED_REP")
    rep("MDT_FILTERED", 10, start=tomorrow, code="FUTURE_REP")
    rep("MDT_FILTERED", 16, cost="EXPIRED_DEPARTMENT")
    rep("MDT_FILTERED", 5, cost="DUMMY")
    rep("MDT_FILTERED", 17, cost="PREFIX_COLLISION")
    rep("MDT_FILTERED", 99, dep_id="HP_MISSING_TA01", code="MISSING_MASTER")
    rep("MDT_NO_CURRENT", 9, end=yesterday, code="EXPIRED_REP")
    rep("MDT_NO_CURRENT", 10, start=tomorrow, code="FUTURE_REP")
    rep("MDT_NO_CURRENT", 16, cost="EXPIRED_DEPARTMENT")
    rep("MDT_NO_CURRENT", 5, cost="DUMMY")
    rep("MDT_TODAY", 8, start=str(today), end=str(today), code="HP")
    rep("MDT_NULL_DATES", 8, start=None, end=None, cost="HP")
    rep("MDT_DUPLICATE", 8, cost="HP")
    rep("MDT_DUPLICATE", 8, code="HP")
    rep("MDT_LOWER", 18, code="HP")
    rep("MDT_SHARED", 8, company="ag01", cost="HP")
    rep("MDT_SHARED", 11, company="aa05", cost="TW")
    person("REP_A", "สมชาย", "ใจดี", "ชาย")
    person("REP_A", "Alternate", "Name")
    person("REP_B", " Somsri ", "Dee", " ")
    person("REUSED_EMPLOYEE", "First", "Company")
    person("REUSED_EMPLOYEE", "Second", "Company", company="aa05")
    person("PERSON_ONLY", "Person", "Only")
    person("NAMED_DEPARTMENT", None, None)
    invoice = table("dimension_view", "view_dim_invoice", {
        "companyID": "STRING", "CustomerReportName": "STRING", "mihCus": "STRING",
        "mix_date": "DATETIME", "mihVnos": "STRING", "mihDep": "STRING",
    })
    customers = table("dimension_view", "view_dim_customer", {
        "companyID": "STRING", "debcode": "STRING", "debnamet": "STRING",
        "FlagMDSNickName": "BOOLEAN", "NicknameCustomer": "STRING",
    })
    debs = table("validated_mac5", "deb", {
        "company_id": "STRING", "debcode": "STRING", "debsalesp": "STRING", "debdate": "DATETIME",
        "debgroup": "STRING",
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
    mdt_expected = {}

    def shop(name, employee="REP_A", *, company="ag01", code=None, own=None, date=None,
             vnos="V001", nickname=None, channel="DC", debdate=None, ta="TA_A", source="DEBSALESP",
             debgroup=None):
        code = code or "".join(name.split())
        date = date or f"{today} 10:00:00"
        invoice.append({"companyID": company, "CustomerReportName": name, "mihCus": code,
                        "mix_date": date, "mihVnos": vnos})
        if not any(c["companyID"] == company and c["debcode"] == code for c in customers):
            customers.append({"companyID": company, "debcode": code, "debnamet": own or name,
                              "FlagMDSNickName": nickname is not None, "NicknameCustomer": nickname})
            debs.append({"company_id": company, "debcode": code, "debsalesp": employee,
                         "debdate": debdate or f"{today} 00:00:00", "debgroup": debgroup})
            if channel is not None:
                quotes.append({"company_id": company, "agent1": code + " customer", "channel": channel,
                               "dinsert": f"{today} 00:00:00", "id": str(len(quotes) + 1)})
        expected[(company, "".join(name.split()))] = {"TADepartmentID": ta, "TASource": source}
        if employee and employee.startswith("MDT_"):
            mdt_expected[(company, "".join(name.split()))] = {
                "TAEmployeeID": None if source == "MDS" else employee,
                "TADebcode": None if source == "MDS" else code,
            }

    def mds(name, department, *, tier="GOLD", active=True, updated=None, ident=None,
            flag_pc=True, online_percent="25.5"):
        masters.append({"companyID": "ag01", "CustomerReportName": name, "DepartmentID": department,
                        "CustomerTier": tier, "FlagPC": flag_pc, "ShopOnline": "Online shop",
                        "OnlinePercent": online_percent, "id": ident or name, "is_active": active,
                        "updated_at": updated or f"{today}T00:00:00Z"})

    shop("ชื่อ XX", code="A4566666", date=f"{yesterday} 10:00:00")
    shop("ชื่อ XX", "REP_B", code="A05699", own="ชื่อ XY", channel="DA")
    expected[("ag01", "ชื่อXX")].update(TADepartmentID="TA_A")
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
    mds("MDS Chain Priority", "TA_MDS", flag_pc=False, online_percent="0")
    shop("Invalid MDS Fallback")
    mds("Invalid MDS Fallback", "TA_NOT_FOUND")
    shop("Inactive MDS")
    mds("Inactive MDS", "TA_MDS", active=False)
    mds("MDS Only", "TA_MDS", flag_pc=None, online_percent="100")
    expected[("ag01", "MDSOnly")] = dict(TADepartmentID="TA_MDS", TASource="MDS")
    shop("Person Only", "PERSON_ONLY", ta=None, source=None)
    shop("Named Department", "NAMED_DEPARTMENT", ta=None, source=None)
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
    shop("MDT Single Chain TA", "MDT_ONE", debgroup="HPEXPO", ta="HP_BK1_TA01", source="MDT")
    shop("MDT Expired Chain TA", "MDT_ONE", debgroup="TW", ta=None, source=None)
    shop("MDT Regional TAs", "MDT_SPLIT", debgroup="HP", ta=None, source=None)
    shop("MDT Not A Chain", "MDT_ONE", debgroup="SCG", ta=None, source=None)
    shop("MDT Blank Group", "MDT_ONE", ta=None, source=None)
    for group, ta in (("HP", "HP_BK1_TA01"), ("HPEXPO", "HP_BK1_TA01"),
                      ("TW", "TW_E01_TA01"), ("TWEXPO", "TW_E01_TA01"),
                      ("BT", "BT_BK1_TA01"), ("BT.C", "BT_BK1_TA01"),
                      ("GB", "GB_BK1_TA01"), ("MH", "MH_BK1_TA01"), ("DOHOME", "DH_BK1_TA01")):
        shop("MDT Mapping " + group, "MDT_ALL_CHAINS", debgroup=group, ta=ta, source="MDT")
    shop("MDT Filtered Candidates", "MDT_FILTERED", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    shop("MDT No Current Candidates", "MDT_NO_CURRENT", debgroup="HP", ta=None, source=None)
    shop("MDT Today Inclusive", "MDT_TODAY", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    shop("MDT Null Dates", "MDT_NULL_DATES", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    shop("MDT Duplicate Department", "MDT_DUPLICATE", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    shop("MDT Lower Department", "MDT_LOWER", debgroup="HP", ta="hp_lower_TA01", source="MDT")
    for label, group in (("Empty", ""), ("Lowercase", "hp"), ("Prefix", "HPX")):
        shop("MDT Invalid Group " + label, "MDT_ALL_CHAINS", debgroup=group, ta=None, source=None)
    shop("MDT Shared Company", "MDT_SHARED", code="MDT_SHARED_CODE", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    shop("MDT Shared Company", "MDT_SHARED", code="MDT_SHARED_CODE", company="aa05", debgroup="HP", ta=None, source=None)
    shop("MDT Other Company TW", "MDT_SHARED", company="aa05", debgroup="TW", ta="TW_E01_TA01", source="MDT")
    shop("MDT MDS Wins", "MDT_ALL_CHAINS", debgroup="HP", ta="TA_MDS", source="MDS")
    mds("MDT MDS Wins", "TA_MDS")
    shop("MDT Missing MDS Department", "MDT_ALL_CHAINS", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    mds("MDT Missing MDS Department", "TA_NOT_FOUND")
    shop("MDT Blank MDS Department", "MDT_ALL_CHAINS", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    mds("MDT Blank MDS Department", None)
    shop("MDT Name Mismatch", "MDT_ALL_CHAINS", debgroup="HP", own="Different legal name", ta=None, source=None)
    mdt_expected[("ag01", "MDTNameMismatch")] = {"TAEmployeeID": None, "TADebcode": None}
    shop("โฮมโปรดักส์ เซ็นเตอร์ สาขาเมกาโฮม-ทดสอบ", "MDT_ALL_CHAINS", debgroup="HP", ta="HP_BK1_TA01", source="MDT")
    invoice[-1]["mihDep"] = "MH_BK1_TA01"
    shop("Plain Chain Group", debgroup="HP")
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
    mds("Dup  Name", "TA_MDS", tier="GOLD", ident="NEW_MASTER", online_percent=None)
    expected[("ag01", "DupName")].update(TADepartmentID="TA_MDS", TASource="MDS")
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
        shutil.copy(repo / VIEW_SOURCE, project / "definitions" / f"{VIEW_ACTION}.sqlx")
        shutil.copy(repo / "definitions/initial/create_all_function.sqlx", project / "definitions/create_all_function.sqlx")
        declared = {"dim_company", "dim_department_last", "update_sk_sale_rep_group", "dim_customer_segment",
                    "dim_sale_representative_last", "dim_invoice", "dim_aging", "dim_order", "dim_customer", "dim_group_customer",
                    "dim_section_last", "dim_region_last", "dim_section_manager_last", "dim_region_manager_last", "dim_director_last"}
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
    _, _, employee_before_sql = compile_action("before-employee", EMPLOYEE_BEFORE_FIX)
    acceptance_project, _, _ = compile_action("acceptance-base", ACCEPTANCE_BASE)
    _, _, mdt_before_sql = compile_action("before-mdt", MDT_BEFORE_CHANGE)
    project, graph, _ = compile_action("target")
    view_sql = next(t for t in graph["tables"] if t["target"]["name"] == VIEW_ACTION)["query"]
    (args.evidence / "target-view-compiled.sql").write_text(view_sql)
    functions = next(o for o in graph["operations"] if o["target"]["name"] == "create_all_function")
    # Execute the compiler-emitted final SQL UDF, clean_company_prefix.
    udf_sql = "CREATE OR REPLACE FUNCTION" + "\n".join(functions["queries"]).rsplit("CREATE OR REPLACE FUNCTION", 1)[1]
    query(udf_sql)
    before_rows, _ = query(before_sql)
    narrowed_rows, _ = query(narrowed_sql)
    employee_before_raw, _ = query(employee_before_sql)
    mdt_before_rows, _ = query(mdt_before_sql)
    employee_before_rows, _ = query(view_sql.replace(
        f"`{PROJECT}.dimension_table.{ACTION}`", f"({employee_before_sql})"))
    env = dict(os.environ, BIGQUERY_EMULATOR_HOST=f"{endpoint}/bigquery/v2")
    # A custom endpoint makes the official BigQuery client omit authentication.
    for key in ("GOOGLE_APPLICATION_CREDENTIALS", "CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE"):
        env.pop(key, None)

    def run_action(action_project, action=ACTION):
        credentials = action_project / ".df-credentials.json"
        credentials.write_text(json.dumps({"projectId": PROJECT, "location": "us-central1"}))
        command = [str(cli), "run", str(action_project), "--actions", action, "--credentials", str(credentials)]
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
    run_action(acceptance_project)
    acceptance_rows, _ = query(f"SELECT * FROM `{PROJECT}.dimension_table.{ACTION}` ORDER BY CustomerReportInfoSK")
    (args.evidence / "acceptance-base-rows.json").write_text(json.dumps(acceptance_rows, ensure_ascii=False, indent=2))
    run_action(project)
    raw_rows, fields = query(f"SELECT * FROM `{PROJECT}.dimension_table.{ACTION}` ORDER BY CustomerReportInfoSK")
    run_action(project, VIEW_ACTION)
    actual_rows, view_fields = query(
        f"SELECT * FROM `{PROJECT}.dimension_view.{VIEW_ACTION}` ORDER BY CustomerReportInfoSK")
    dep_by_sk = {d["DepartmentSK"]: d for d in departments}
    rep_by_sk = {r["SaleRepSK"]: r for r in reps}
    deb_by_code = {(d["company_id"], d["debcode"]): d for d in debs}

    def index(rows):
        return {(r["CompanyID"], "".join(r["CustomerReportName"].split())): r for r in rows}

    actual = index(actual_rows)
    raw = index(raw_rows)
    # Shops of MDT employees gain a TA in this change; earlier commits are compared on the rest.
    mdt_keys = set(mdt_expected)
    before = index(before_rows)
    base = index(base_rows)
    removed = index(removed_rows)
    narrowed = index(narrowed_rows)
    employee_before = index(employee_before_rows)
    employee_before_table = index(employee_before_raw)
    mdt_before = index(mdt_before_rows)
    (args.evidence / "before-mdt-rows.json").write_text(json.dumps(mdt_before_rows, ensure_ascii=False, indent=2))
    (args.evidence / "materialized-target-table-rows.json").write_text(json.dumps(raw_rows, ensure_ascii=False, indent=2))
    (args.evidence / "materialized-target-rows.json").write_text(json.dumps(actual_rows, ensure_ascii=False, indent=2))
    (args.evidence / "base-rows.json").write_text(json.dumps(base_rows, ensure_ascii=False, indent=2))
    (args.evidence / "before-r2-rows.json").write_text(json.dumps(before_rows, ensure_ascii=False, indent=2))
    (args.evidence / "narrowed-trace-rows.json").write_text(json.dumps(narrowed_rows, ensure_ascii=False, indent=2))
    (args.evidence / "target-schema.json").write_text(json.dumps(fields, indent=2))
    (args.evidence / "target-view-schema.json").write_text(json.dumps(view_fields, indent=2))
    (args.evidence / "before-employee-rows.json").write_text(json.dumps(employee_before_rows, ensure_ascii=False, indent=2))
    failures = []
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(name)

    check("output has exactly one row per company and whitespace-normalized name",
          len(raw_rows) == len(actual_rows) == len(actual) == len(expected) and actual.keys() == expected.keys(),
          {"rows": len(actual_rows), "expected": len(expected)})
    for key, values in expected.items():
        observed = {k: actual.get(key, {}).get(k) for k in values}
        check(f"TA selection: {key[0]} / {key[1]}", observed == values, {"expected": values, "actual": observed})
    stable_columns = ("CustomerReportInfoSK", "CompanySK", "CustomerSegmentSK", "CompanyID", "CustomerReportName",
                      "FlagPC", "ShopOnline", "OnlinePercent", "SegmentSource", "SegmentDebcode", "SegmentChannel", "MdsID")
    retained_columns = stable_columns + ("TASource", "TADebcode")
    check("TA and segment values are preserved from the configured acceptance base",
          index(acceptance_rows).keys() == raw.keys() and all(
              {k: actual[key]["TADepartmentID"] if k == "DepartmentID" else raw[key][k] for k in row} == row
              for key, row in index(acceptance_rows).items() if key not in mdt_keys), acceptance_rows)
    stable = raw.keys() == base.keys() and all(
        {k: r[k] for k in retained_columns} == {k: raw[key][k] for k in retained_columns}
        for key, r in base.items() if key not in mdt_keys)
    check("every retained value, including TA lookup code, equals base output",
          stable, {"columns": retained_columns})
    for name, segment, source in (("ชื่อ XX", 1002, "CHANNEL"), ("SCG Branch", 1001, "CHANNEL"),
                                  ("TT Current Month", 1004, "CHANNEL"), ("TT Previous Month", 1005, "CHANNEL"),
                                  ("Unknown Tier", 1001, "DEFAULT"), ("No Channel", 1001, "DEFAULT"),
                                  ("Channel Guard", 1002, "CHANNEL"), ("MDS Priority", 1003, "MDS")):
        row = actual[("ag01", "".join(name.split()))]
        check(f"segment contract: {name}", (row["CustomerSegmentSK"], row["SegmentSource"]) == (segment, source), row)
    ta_sk_columns = ["DepartmentSK", "SectionSK", "RegionSK", "SectionManagerSK", "RegionManagerSK", "DirectorSK"]
    mdt_changed_columns = set(ta_sk_columns) | {"TASource"}
    check("MDT fallback changes only the selected TA hierarchy and source relative to the branch base",
          raw.keys() == mdt_before.keys() and all(
              {k: v for k, v in row.items() if k not in mdt_changed_columns}
              == {k: v for k, v in mdt_before[key].items() if k not in mdt_changed_columns}
              for key, row in raw.items()), {"allowed_changes": sorted(mdt_changed_columns)})
    check("MDT fallback leaves every non-MDT customer-report row identical to the branch base",
          all(row == mdt_before[key] for key, row in raw.items() if key not in mdt_keys),
          {"non_mdt_rows": len(raw) - len(mdt_keys)})
    check("the missing chain TA is reproduced before this change and resolved by the running product",
          all(mdt_before[key]["DepartmentSK"] is None and mdt_before[key]["TASource"] is None
              and raw[key]["DepartmentSK"] is not None and raw[key]["TASource"] == "MDT"
              for key in mdt_keys if expected[key]["TASource"] == "MDT"),
          [{"before": mdt_before[key], "after": raw[key]}
           for key in mdt_keys if expected[key]["TASource"] == "MDT"])
    expected_schema = list(stable_columns) + ta_sk_columns + ["TASource", "TADebcode", "SaleRepSK"]
    removed_columns = ("DepartmentID", "TAEmployeeID", "TAEmployeeName")
    check("TA chain SKs all come from the chosen dim_department_last row",
          all({c: r[c] for c in ta_sk_columns} == ({c: dep_by_sk[r["DepartmentSK"]][c] for c in ta_sk_columns}
              if r["DepartmentSK"] is not None else dict.fromkeys(ta_sk_columns)) for r in raw_rows), raw_rows)
    chain_information = {
        "TADepartmentID": "TA_A", "TADepartmentName": "TA_A name",
        "TASectionID": "SECTION", "TASectionName": "Section name",
        "TARegionID": "REGION", "TARegionName": "Region name",
        "TASectionManagerID": "SM", "TASectionManagerName": "Section Manager",
        "TARegionManagerID": "RM", "TARegionManagerName": "Region Manager (Boss)",
        "TADirectorID": "DIRECTOR", "TADirectorName": "Director name",
    }
    check("a plain view SELECT exposes the selected hierarchy IDs and formatted names",
          {c: actual[("ag01", "ชื่อXX")][c] for c in chain_information} == chain_information,
          actual[("ag01", "ชื่อXX")])
    view_columns = expected_schema + list(chain_information) + ["TAEmployeeID", "TAEmployeeName"]
    check("the public view adds only hierarchy and employee information, with no segment or director-manager enrichment",
          [f["name"] for f in view_fields] == view_columns, view_fields)
    check("unresolved TA rows expose no hierarchy information",
          all(all(row[c] is None for c in chain_information) for row in actual_rows if row["DepartmentSK"] is None),
          [row for row in actual_rows if row["DepartmentSK"] is None])
    for row in raw_rows:
        employee = deb_by_code.get((row["CompanyID"], row["TADebcode"]), {}).get("debsalesp")
        candidates = [r for r in reps if employee is not None
                      and r["CompanySK"] == row["CompanySK"] and r["EmployeeID"] == employee]
        chosen = min(candidates, key=lambda r: (r.get("EmployeeName") is None, r["SaleRepSK"])) if candidates else None
        check(f"independent employee selection: {row['CompanyID']} / {row['CustomerReportName']}",
              row["SaleRepSK"] == (chosen["SaleRepSK"] if chosen else None), row)
    check("employee selection preserves every other table value including all TA chain SKs",
          raw.keys() == employee_before_table.keys() and all(
              {k: v for k, v in r.items() if k != "SaleRepSK"}
              == {k: v for k, v in employee_before_table[key].items() if k != "SaleRepSK"}
              for key, r in raw.items() if key not in mdt_keys), raw_rows)
    for company, name, employee, full_name in (
            ("ag01", "ชื่อXX", "REP_A", "สมชาย ใจดี (ชาย)"),
            ("ag01", "LatestMatching", "REP_B", "Somsri Dee"),
            ("ag01", "PersonOnly", "PERSON_ONLY", "Person Only"),
            ("ag01", "NamedDepartment", "NAMED_DEPARTMENT", "Named Department (ND)"),
            ("ag01", "CompanyBoundary", "REUSED_EMPLOYEE", "First Company"),
            ("aa05", "CompanyBoundary", "REUSED_EMPLOYEE", "Second Company")):
        row = actual[(company, name)]
        check(f"view resolves employee ID and formatted name: {company} / {name}",
              (row["TAEmployeeID"], row["TAEmployeeName"]) == (employee, full_name), row)
    for name, employee in (("SingleCostChain", "CHAIN_COST"), ("SingleDepcodeChain", "CHAIN_CODE"),
                           ("PlainMultiple", "PLAIN_MULTI"), ("ExpiredRep", "REP_EXPIRED"),
                           ("FutureRep", "REP_FUTURE")):
        row = actual[("ag01", name)]
        check(f"view retains employee identity for an unresolved TA without a name: {name}",
              row["TADepartmentID"] is None and row["TAEmployeeID"] == employee
              and row["TAEmployeeName"] is None and row["SaleRepSK"] in rep_by_sk, row)
    check("employee-selection regression is reproduced before the fix and corrected through the view",
          employee_before[("ag01", "SingleCostChain")]["SaleRepSK"] is None
          and actual[("ag01", "SingleCostChain")]["TAEmployeeID"] == "CHAIN_COST"
          and employee_before[("ag01", "ชื่อXX")]["TAEmployeeName"] is None
          and actual[("ag01", "ชื่อXX")]["TAEmployeeName"] == "สมชาย ใจดี (ชาย)",
          {"before": employee_before[("ag01", "ชื่อXX")], "after": actual[("ag01", "ชื่อXX")]})
    check("TAEmployeeID is NULL for MDS rows and only set alongside TADebcode",
          all(r["TAEmployeeID"] is None for r in actual_rows if r["TASource"] == "MDS")
          and all(r["TADebcode"] is not None for r in actual_rows if r["TAEmployeeID"] is not None)
          and actual[("ag01", "NoDebsalesp")]["TAEmployeeID"] is None, actual_rows)
    check("TAEmployeeID keeps the debsalesp employee of the lookup code",
          actual[("ag01", "ชื่อXX")]["TAEmployeeID"] == "REP_A", actual[("ag01", "ชื่อXX")])
    missing_employee, _ = query(
        f"SELECT cri.TADebcode, cri.SaleRepSK, cri.TAEmployeeID, cri.TAEmployeeName, deb.debsalesp "
        f"FROM `{PROJECT}.dimension_view.{VIEW_ACTION}` AS cri "
        f"LEFT JOIN `{PROJECT}.validated_mac5.deb` AS deb "
        "ON cri.CompanyID = deb.company_id AND cri.TADebcode = deb.debcode "
        "WHERE cri.CustomerReportName = 'Missing Rep'")
    check("a missing employee remains SK-only while its raw employee code is traceable through TADebcode",
          missing_employee == [{"TADebcode": "MissingRep", "SaleRepSK": None, "TAEmployeeID": None,
                                "TAEmployeeName": None, "debsalesp": "NO_SUCH_REP"}], missing_employee)
    check("TADebcode is NULL when MDS supplies the TA",
          all(r["TADebcode"] is None for r in actual_rows if r["TASource"] == "MDS"), actual_rows)
    check("TADebcode keeps the customer code that supplied the TA",
          actual[("ag01", "ชื่อXX")]["TADebcode"] == "A4566666", actual[("ag01", "ชื่อXX")])
    for name in ("NoDebsalesp", "MissingRep", "MissingDeb", "PlainMultiple", "SingleCostChain",
                 "ExpiredDepartment", "DummyOnly", "ExpiredRep", "FutureRep", "LatestUnusable"):
        row = actual[("ag01", name)]
        code = "CHAIN_LATEST" if name == "LatestUnusable" else name
        check(f"diagnostic customer code survives unresolved TA: {name}",
              row["TADepartmentID"] is None and row["TASource"] is None and row["TADebcode"] == code, row)
    for name in ("SCGBranch", "CRCBranch", "MecBranch"):
        check(f"a mismatched customer name cannot supply a TA lookup code: {name}",
              actual[("ag01", name)]["TADebcode"] is None, actual[("ag01", name)])
    check("diagnostic-code regression reproduced before review fix and corrected",
          narrowed[("ag01", "NoDebsalesp")]["TADebcode"] is None
          and actual[("ag01", "NoDebsalesp")]["TADebcode"] == "NoDebsalesp",
          {"before": narrowed[("ag01", "NoDebsalesp")], "after": actual[("ag01", "NoDebsalesp")]})
    check("immediate base table omits both TA trace columns",
          [f["name"] for f in removed_fields] == list(stable_columns) + ["DepartmentID", "TASource"], removed_fields)
    check("rebuilding the immediate base swaps DepartmentID for TA SKs and adds TADebcode and SaleRepSK",
          [f["name"] for f in fields] == expected_schema
          and all(f["type"] == "INTEGER" for f in fields if f["name"] in ta_sk_columns + ["SaleRepSK"]), fields)
    check("all existing values equal the immediate base output after restoration",
          removed.keys() == raw.keys() and all(
              {k: actual[key]["TADepartmentID"] if k == "DepartmentID" else raw[key][k] for k in row} == row
              for key, row in removed.items() if key not in mdt_keys),
          {"columns": [f["name"] for f in removed_fields]})
    check("base materialized table reproduces exposed employee and TA customer codes",
          all(c in {f["name"] for f in base_fields} for c in ("TAEmployeeID", "TADebcode"))
          and any(all(row[c] is not None for c in ("TAEmployeeID", "TADebcode")) for row in base_rows), base_fields)
    check("rebuilding the existing table exposes TA SKs, TADebcode and SaleRepSK",
          [f["name"] for f in fields] == expected_schema, fields)
    check("all retained column types equal the base materialized schema",
          [f for f in fields if f["name"] in retained_columns]
          == [f for f in base_fields if f["name"] in retained_columns], fields)
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
          rerun_fields == fields and rerun_rows == raw_rows, {"schema": rerun_fields, "rows": len(rerun_rows)})
    # The reporting view must pass through the segment SK without consulting the
    # segment dimension, which Power BI already relates separately.
    query(f"DELETE FROM `{PROJECT}.dimension_table.dim_customer_segment` WHERE TRUE")
    segment_independent_rows, _ = query(
        f"SELECT * FROM `{PROJECT}.dimension_view.{VIEW_ACTION}` ORDER BY CustomerReportInfoSK")
    check("the deployed view still returns identical rows when the segment dimension is empty",
          segment_independent_rows == actual_rows, segment_independent_rows)
    # Information belongs to the view: change the selected name at its source,
    # without rebuilding the customer-report table, and observe it immediately.
    selected_sk = actual[("ag01", "ชื่อXX")]["SaleRepSK"]
    query(f"UPDATE `{PROJECT}.dimension_table.dim_sale_representative_last` "
          f"SET EmployeeName = 'Updated', EmployeeSurname = 'Person', EmployeeNickname = NULL WHERE SaleRepSK = {selected_sk}")
    updated_employee, _ = query(
        f"SELECT TAEmployeeID, TAEmployeeName FROM `{PROJECT}.dimension_view.{VIEW_ACTION}` "
        "WHERE CustomerReportName = 'ชื่อ XX'")
    unchanged_table_rows, _ = query(f"SELECT * FROM `{PROJECT}.dimension_table.{ACTION}` ORDER BY CustomerReportInfoSK")
    check("the deployed view reflects an employee-name update without persisting employee information in the table",
          updated_employee == [{"TAEmployeeID": "REP_A", "TAEmployeeName": "Updated Person"}]
          and unchanged_table_rows == raw_rows, {"view": updated_employee, "table_unchanged": unchanged_table_rows == raw_rows})
    for key in (("ag01", "SingleCostChain"), ("ag01", "SingleDepcodeChain"),
                ("ag01", "ExpiredChain"), ("ag01", "DanglingExpiredChain"), ("ag01", "FutureChain")):
        check(f"R2 regression reproduced before fix and corrected: {key[1]}",
              before[key]["DepartmentID"] is not None and actual[key]["TADepartmentID"] is None,
              {"before": before[key], "after": actual[key]})
    check("MDS fields retain their stored types and values in the table",
          raw[("ag01", "MDSPriority")]["FlagPC"] is True
          and raw[("ag01", "MDSPriority")]["OnlinePercent"] == 25.5
          and raw[("ag01", "MDSPriority")]["ShopOnline"] == "Online shop",
          raw[("ag01", "MDSPriority")])
    check("the view exposes FlagPC as STRING and OnlinePercent as FLOAT",
          {f["name"]: f["type"] for f in view_fields if f["name"] in ("FlagPC", "OnlinePercent")}
          == {"FlagPC": "STRING", "OnlinePercent": "FLOAT"}, view_fields)
    for name, flag_pc, online_percent in (
            ("MDSPriority", "Yes", 0.255), ("MDSChainPriority", "No", 0.0),
            ("MDSOnly", "No", 1.0), ("DupName", "Yes", None), ("NoChannel", "No", None)):
        row = actual[("ag01", name)]
        check(f"view converts FlagPC and OnlinePercent for Power BI: {name}",
              (row["FlagPC"], row["OnlinePercent"]) == (flag_pc, online_percent), row)
    check("every reporting row has a non-null Yes/No FlagPC",
          all(row["FlagPC"] in ("Yes", "No") for row in actual_rows), actual_rows)
    check("MDT shops keep the debsalesp employee and lookup code whether or not a chain TA resolves",
          all({c: actual[key][c] for c in values} == values for key, values in mdt_expected.items()),
          [actual[key] for key in mdt_keys])
    check("an MDT TA carries its full hierarchy",
          raw[("ag01", "MDTSingleChainTA")]["SectionSK"] == 10, raw[("ag01", "MDTSingleChainTA")])
    check("the reporting view preserves ShopOnline",
          all(actual[key]["ShopOnline"] == row["ShopOnline"] for key, row in raw.items()), actual_rows)
    (args.evidence / "behavior-checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2))
    (args.evidence / "query-responses.json").write_text(json.dumps(responses, ensure_ascii=False, indent=2))
    print(json.dumps({"failures": failures, "fixture_date": str(today), "materialized_rows": len(actual_rows),
                      "evidence": str(args.evidence)}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

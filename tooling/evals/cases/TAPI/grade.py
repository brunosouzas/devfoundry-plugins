"""Script items of the TAPI rubric (grading.md): A1 (params part), A2, C3 (script part), D1 (namespace part),
E2 (counts), F1 (each profile rule). E1 is the build itself. The review items are not here (review-brief.md).
Usage: python3 -I grade.py <run project dir> [<fixture dir>]   -> one line per item and a JSON summary.
The fixture defaults to the case's own fixture/, so only what the run added is graded."""
import json, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

proj = Path(sys.argv[1])
tmpl = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent / "fixture"
CORE = "http://www.mulesoft.org/schema/mule/core"
EE = "http://www.mulesoft.org/schema/mule/ee/core"
MUNIT = "http://www.mulesoft.org/schema/mule/munit"
results, notes = {}, []

def rel(p, root): return str(p.relative_to(root))

def parse(path):
    txt = path.read_text(errors="replace")
    try:
        return ET.fromstring(txt.encode())
    except ET.ParseError:
        # unbound prefixes (doc:) break the stdlib parser: bind them and retry
        txt2 = re.sub(r"<mule\b", '<mule xmlns:doc="http://www.mulesoft.org/schema/mule/documentation"', txt, count=1)
        try: return ET.fromstring(txt2.encode())
        except ET.ParseError as e:
            notes.append(f"parse error {path}: {e}"); return None

def mule_files(root, sub="src/main/mule"):
    return sorted((root / sub).rglob("*.xml")) if (root / sub).exists() else []

def local(tag): return tag.split("}")[-1]

def collect(root):
    """Facts about the Mule code of a project."""
    f = {"flows": {}, "subflows": {}, "globals": [], "vars": set(), "errors": set()}
    for p in mule_files(root):
        r = parse(p)
        if r is None: continue
        for child in r:
            tag = child.tag
            if tag == f"{{{CORE}}}flow": f["flows"][child.get("name")] = rel(p, root)
            elif tag == f"{{{CORE}}}sub-flow": f["subflows"][child.get("name")] = rel(p, root)
            elif not isinstance(tag, str): continue
            else:
                f["globals"].append((local(tag), child.get("name") or child.get("file") or child.get("doc:name"), rel(p, root)))
        for el in r.iter():
            if not isinstance(el.tag, str): continue
            if local(el.tag) == "set-variable" and el.get("variableName"): f["vars"].add(el.get("variableName"))
            if el.get("target") and local(el.tag) not in ("set-variable",): f["vars"].add(el.get("target"))
            if local(el.tag) == "raise-error" and el.get("type"): f["errors"].add(el.get("type"))
            if local(el.tag) == "error-mapping" and el.get("targetType"): f["errors"].add(el.get("targetType"))
    return f

def props(root):
    keys, text = set(), ""
    # Property files only (src/main/resources/properties/): a data file in YAML (a list the code reads) is not properties.
    for p in sorted((root / "src/main/resources/properties").rglob("*.yaml")) if (root / "src/main/resources/properties").exists() else []:
        t = p.read_text(errors="replace"); text += t
        stack = []
        for line in t.splitlines():
            if not line.strip() or line.lstrip().startswith(("#", "-")): continue
            m = re.match(r"^(\s*)([\"']?[\w.\-]+[\"']?)\s*:", line)
            if not m: continue
            ind = len(m.group(1)); key = m.group(2).strip("\"'")
            while stack and stack[-1][0] >= ind: stack.pop()
            stack.append((ind, key)); keys.add(".".join(k for _, k in stack))
    return keys, text

P, T = collect(proj), collect(tmpl)
pk, ptext = props(proj); tk, _ = props(tmpl)

def item(k, ok, ev): results[k] = {"pass": bool(ok), "evidence": ev}

# A1 (script part): a spec with the params
# Every file of the API folder: the spec and the fragments, types or schemas it references.
api_dir = proj / "src/main/resources/api"
spec_files = [p for p in api_dir.rglob("*") if p.is_file()] if api_dir.exists() else []
need = ["/jobs", "jobRef", "dateFrom", "dateTo", "searchType", "DATE-RANGE-SEARCH", "filter", "CUSTOMER-NOTIFY",
        "safetyFlags", "hasPortal", "badgeNumber", "inspections", "lastCustomerUpdate"]
spec_text = "".join(p.read_text(errors="replace") for p in spec_files)
missing = [n for n in need if n not in spec_text]
item("A1-script", spec_files and not missing, {"spec": [rel(p, proj) for p in spec_files], "missing": missing})

# A2: APIkit flows for both endpoints
ak = [n for n in P["flows"] if n and n.startswith("get:\\jobs")]
item("A2", any(re.fullmatch(r"get:\\jobs:.*", n) for n in ak) and any(re.search(r"get:\\jobs\\\(jobRef\):", n) for n in ak), ak)

# C3 (script part): changeable lists outside the code: in properties or in a data file under src/main/resources
# (a JSON, CSV or YAML file the code reads by a property), never written in a flow or a DataWeave script.
markers = {"safetyFlag": "HAZ", "noteSubType": "CU_OUTBOUND", "contractor": "5100000000000000000901",
           "jobTypeId": "9001000000000000000012"}
res = proj / "src/main/resources"
prop_dir = res / "properties"
prop_text = "".join(p.read_text(errors="replace") for p in prop_dir.rglob("*") if p.is_file()) if prop_dir.exists() else ""
# A data file counts when a property names it (its file name appears in the property files).
data_files = [p for p in res.rglob("*") if p.is_file() and p.suffix in (".json", ".csv", ".yaml", ".yml")
              and prop_dir not in p.parents and p.name in prop_text] if res.exists() else []
data_text = prop_text + "".join(p.read_text(errors="replace") for p in data_files)
code_text = "".join(p.read_text(errors="replace") for p in mule_files(proj)) + ("".join(
    p.read_text(errors="replace") for p in res.rglob("*.dwl")) if res.exists() else "")
c3 = {k: {"in_data": v in data_text, "hard_coded": v in code_text} for k, v in markers.items()}
item("C3-script", all(x["in_data"] and not x["hard_coded"] for x in c3.values()), c3)

# D1 (script part): new custom error types, all WRS:
new_err = sorted(e for e in P["errors"] - T["errors"] if not e.split(":")[0] in ("HTTP", "APIKIT", "MULE", "WSC", "EXPRESSION", "STREAM_MAXIMUM_SIZE_EXCEEDED", "OS", "ANY"))
item("D1-script", new_err and all(e.startswith("WRS:") for e in new_err), new_err)

# E2 (counts): MUnit tests in new suites, mocks
def munit_tests(root):
    names, mocks_by_file = {}, {}
    for p in sorted((root / "src/test/munit").rglob("*.xml")) if (root / "src/test/munit").exists() else []:
        r = parse(p)
        if r is None: continue
        for el in r.iter():
            if isinstance(el.tag, str) and el.tag == f"{{{MUNIT}}}test": names[el.get("name")] = rel(p, root)
        mocks_by_file[rel(p, root)] = sum(1 for el in r.iter() if isinstance(el.tag, str) and local(el.tag) == "mock-when")
    return names, mocks_by_file
pt, pm = munit_tests(proj); tt, tm = munit_tests(tmpl)
new_tests = {n: f for n, f in pt.items() if n not in tt}
tests = len(new_tests); mocks = sum(m - tm.get(f, 0) for f, m in pm.items())
suites = sorted({(f, sum(1 for x in new_tests.values() if x == f)) for f in new_tests.values()})
item("E2-counts", tests >= 4 and mocks >= 1, {"suites": suites, "tests": tests, "mocks": mocks})

# F1: each profile rule, on new code only
f1 = {}
new_flows = {n: f for n, f in P["flows"].items() if n not in T["flows"] and ":" not in (n or "")}
f1["flow"] = {"pass": bool(new_flows) and all(re.fullmatch(r"wrk-[a-z0-9-]+-(list|get|create|update|delete)-flow", n) for n in new_flows)
              and {"wrk-jobs-list-flow", "wrk-jobs-get-flow"} <= set(new_flows), "new": new_flows}
new_sub = {n: f for n, f in P["subflows"].items() if n not in T["subflows"]}
f1["subflow"] = {"pass": all(re.fullmatch(r"wrk-[a-z0-9-]+-subflow", n) for n in new_sub), "new": new_sub}
f1["implFile"] = {"pass": bool(new_flows) and all(f == "src/main/mule/impl/wrk-jobs.xml" for f in new_flows.values()),
                  "files": sorted(set(new_flows.values()))}
tg = {(t, n, f) for t, n, f, *_ in T["globals"]}
skip = {"flow", "sub-flow"}
new_glob = [(t, n, f) for t, n, f in P["globals"] if (t, n, f) not in tg and t not in skip]
f1["globalConfigFile"] = {"pass": bool(new_glob) and all(f == "src/main/mule/common/wrk-global.xml" for _, _, f in new_glob), "new": new_glob}
new_vars = sorted(P["vars"] - T["vars"] - {"httpStatus", "outboundHeaders"})  # the template's listener and APIkit contract variables
f1["variable"] = {"pass": bool(new_vars) and all(re.fullmatch(r"wrk[A-Z][A-Za-z0-9]*", v) for v in new_vars), "new": new_vars}
dwl_new = [rel(p, proj) for p in (proj / "src/main/resources").rglob("*.dwl") if not (tmpl / rel(p, proj)).exists()] if (proj / "src/main/resources").exists() else []
f1["dwlFile"] = {"pass": bool(dwl_new) and all(re.fullmatch(r"src/main/resources/dwl/jobs/[\w.-]+\.dwl", d) for d in dwl_new), "new": dwl_new}
f1["errorNamespace"] = {"pass": results["D1-script"]["pass"], "new": new_err}
new_keys = sorted(k for k in pk - tk if not any(o.startswith(k + ".") for o in pk))  # leaves only
f1["propertyPrefix"] = {"pass": bool(new_keys) and all(k.startswith("wrs.") for k in new_keys), "new": new_keys}
item("F1", all(v["pass"] for v in f1.values()), f1)

for k, v in results.items():
    print(f"{k}: {'PASS' if v['pass'] else 'FAIL'}")
    if k == "F1":
        for r_, x in v["evidence"].items(): print(f"   {r_}: {'PASS' if x['pass'] else 'FAIL'}  {json.dumps({a: b for a, b in x.items() if a != 'pass'})[:300]}")
    else: print("   ", json.dumps(v["evidence"])[:400])
for n in notes: print("NOTE", n)
print("JSON", json.dumps({k: v["pass"] for k, v in results.items()} | {f"F1.{r_}": x["pass"] for r_, x in results["F1"]["evidence"].items()}))

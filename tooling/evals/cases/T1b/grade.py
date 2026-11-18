"""Deterministic part of the T1b rubric (tooling/evals/cases/T1b/grading.md), read from the project a run left.
Usage: python3 grade.py <project dir>... (each a <run>.files folder). Prints one JSON line per project in the
skill-creator grading shape: {"run", "expectations": [{"text", "passed", "evidence"}]}.
- R1 is decided here: a dedup construct keyed on orderId (os:store failIfPresent, idempotent-message-validator, or
  os:contains + os:store on the same key) and a POST /invoices call in the same project.
- R3 passes here when an os:object-store has a finite entryTtl; otherwise passed=null (read the answer, R3 flexible).
- R2 needs judgment: passed=null, with the code signal as evidence (os:remove in an error handler, or a state per key).
  The grader confirms R2 from the code and the answer."""
import glob, json, os, re, sys
import xml.etree.ElementTree as ET
OS, CORE, HTTP = "http://www.mulesoft.org/schema/mule/os", "http://www.mulesoft.org/schema/mule/core", "http://www.mulesoft.org/schema/mule/http"

def elems(root):
    parents = {c: p for p in root.iter() for c in p}
    for e in root.iter():
        yield e, parents

def in_error_handler(e, parents):
    while e in parents:
        e = parents[e]
        if e.tag.split('}')[-1].startswith('on-error'): return True
    return False

def grade(project):
    found = {"claim": [], "validator": [], "contains": [], "store_keys": [], "invoices": [], "ttl": [], "remove_on_error": [], "states": []}
    for f in sorted(glob.glob(os.path.join(project, "src/main/mule/**/*.xml"), recursive=True)):
        rel = os.path.relpath(f, project)
        text = open(f).read()
        try: root = ET.fromstring(text)
        except ET.ParseError as err:
            # Grade the design anyway (the rubric is about the design), and report that the file does not load.
            found.setdefault("parse_errors", []).append(f"{rel}: {err}")
            patched = re.sub(r"<mule\b", '<mule xmlns:doc="http://www.mulesoft.org/schema/mule/documentation"', text, count=1) \
                if 'xmlns:doc=' not in text else text
            try: root = ET.fromstring(patched)
            except ET.ParseError: continue
        for e, parents in elems(root):
            ns, _, tag = e.tag[1:].partition('}') if e.tag.startswith('{') else ("", "", e.tag)
            key = e.get("key", "")
            if ns == OS and tag == "store":
                found["store_keys"].append(key)
                if e.get("failIfPresent") == "true" and "orderId" in key: found["claim"].append(f"{rel}: os:store key={key} failIfPresent")
            if ns == OS and tag == "contains" and "orderId" in key: found["contains"].append(f"{rel}: os:contains key={key}")
            if ns == OS and tag == "remove" and in_error_handler(e, parents): found["remove_on_error"].append(f"{rel}: os:remove key={key} in error handler")
            if ns == OS and tag == "object-store" and e.get("entryTtl"): found["ttl"].append(f"{rel}: {e.get('name')} entryTtl={e.get('entryTtl')} {e.get('entryTtlUnit', '')}")
            if ns == CORE and tag == "idempotent-message-validator" and "orderId" in (e.get("idExpression") or ""):
                found["validator"].append(f"{rel}: idempotent-message-validator idExpression={e.get('idExpression')}")
            if ns == HTTP and tag == "request" and "invoices" in (e.get("path") or ""): found["invoices"].append(f"{rel}: http:request {e.get('method')} {e.get('path')}")
        for s in sorted(set(re.findall(r'"(IN_PROGRESS|PENDING|PROCESSING|DONE|ISSUED|UNKNOWN)"', text))): found["states"].append(f"{rel}: state {s}")
    check_then_act = [c for c in found["contains"] if any("orderId" in k for k in found["store_keys"])]
    dedup = found["claim"] + found["validator"] + check_then_act
    r1 = bool(dedup) and bool(found["invoices"])
    r2_signal = found["remove_on_error"] + sorted(set(found["states"]))
    exp = [
        {"text": "R1 business-key dedup on orderId before POST /invoices", "passed": r1,
         "evidence": "; ".join(dedup + found["invoices"]) or "no dedup construct keyed on orderId, or no POST /invoices"},
        {"text": "R2 failure after the key is stored is handled", "passed": None,
         "evidence": ("code signal: " + "; ".join(r2_signal)) if r2_signal else "no code signal (confirm from the answer and the flow)"},
        {"text": "R3 TTL/window limit (flexible)", "passed": True if found["ttl"] else None,
         "evidence": "; ".join(found["ttl"]) or "no entryTtl in code: read the answer"},
    ]
    if found.get("parse_errors"): exp.append({"text": "XML parses (not graded in R1-R3; T4 builds it)", "passed": False, "evidence": "; ".join(found["parse_errors"])})
    return {"run": project, "expectations": exp}

for p in sys.argv[1:]: print(json.dumps(grade(p.rstrip('/'))))

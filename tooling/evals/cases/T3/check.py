"""Deterministic T3/T3b grader: checks F1-F4 (tooling/evals/cases/T3/grading.md, tooling/evals/cases/T3b/grading.md) on the NEW code only.

Usage: python3 check.py <project dir> <profile.yaml> [--base <fixture dir>]

New code = what the run added compared with --base (the fixture the run started from):
  - new flows / sub-flows: names not present in the base;
  - new global elements: top-level non-flow elements whose (tag, name) is not in the base;
  - new variables: set-variable / target names inside new flows.
Without --base every element counts as new (T3, empty fixture).

No resource name is fixed: for each new endpoint flow (a new flow with an http:listener) the resource is
the first segment of the listener path and the operation comes from the method and the path
(GET + {param} = get, GET = list, POST = create, PUT/PATCH = update, DELETE = delete).
The patterns come from mulesoft.naming of the profile. Exit 0 when every applicable field passes.
F3 is N/A when no global element is new, F4 when no new variable exists.
INFO lines (not graded): legacy flows/files that disappeared (renamed or moved).
"""
import argparse, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

CORE = "{http://www.mulesoft.org/schema/mule/core}"
HTTP = "{http://www.mulesoft.org/schema/mule/http}"
FLOW_TAGS = {CORE + "flow", CORE + "sub-flow"}


def read_naming(path):
    naming, inside, indent = {}, False, None
    for raw in Path(path).read_text().splitlines():
        line = "" if raw.lstrip().startswith("#") else raw.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^\s*naming:\s*$", line):
            inside = True; continue
        if inside:
            m = re.match(r"^(\s+)([A-Za-z]+):\s*(.+)$", line)
            if not m or (indent is not None and len(m.group(1)) != indent):
                break
            indent = len(m.group(1))
            naming[m.group(2)] = m.group(3).strip().strip('"\'')
    return naming


def fill(pattern, resource, operation):
    return (pattern.replace("{resource}", resource.lower()).replace("{RESOURCE}", resource.upper())
            .replace("{operation}", operation.lower()).replace("{OPERATION}", operation.upper()))


# camelCase / PascalCase: no two capitals in a row, so acronyms are written productId, not productID.
CASES = {"camelCase": r"[a-z][a-z0-9]*(?:[A-Z][a-z0-9]+)*", "snake_case": r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*",
         "PascalCase": r"(?:[A-Z][a-z0-9]+)+", "kebab-case": r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"}


def variable_regex(rule):
    if rule in CASES:
        rule = "{" + rule + "}"
    out, pos = "", 0
    for m in re.finditer(r"\{([A-Za-z_-]+)\}", rule):
        out += re.escape(rule[pos:m.start()]) + CASES[m.group(1)]
        pos = m.end()
    return re.compile("^" + out + re.escape(rule[pos:]) + "$")


def operation_of(method, path):
    method = (method or "GET").split(",")[0].strip().upper()
    has_param = "{" in path
    return {"GET": "get" if has_param else "list", "POST": "create", "PUT": "update",
            "PATCH": "update", "DELETE": "delete"}.get(method, method.lower())


def scan(root):
    """flows: name -> (file, element); globals: (tag, name) -> [files]."""
    flows, globals_ = {}, {}
    base = Path(root) / "src/main/mule"
    if not base.is_dir():
        return flows, globals_
    for f in sorted(base.rglob("*.xml")):
        rel = f.relative_to(root).as_posix()
        for el in ET.parse(f).getroot():
            if not isinstance(el.tag, str):
                continue
            if el.tag in FLOW_TAGS:
                flows.setdefault(el.get("name"), []).append((rel, el))
            else:
                key = (el.tag.split("}")[-1], el.get("name") or el.get("file") or "")
                globals_.setdefault(key, []).append(rel)
    return flows, globals_


def variables_in(el):
    out = []
    for e in el.iter():
        if not isinstance(e.tag, str):
            continue
        if e.tag == CORE + "set-variable" and e.get("variableName"):
            out.append(e.get("variableName"))
        if e.get("target"):
            out.append(e.get("target"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project"); ap.add_argument("profile"); ap.add_argument("--base")
    a = ap.parse_args()
    naming = read_naming(a.profile)
    flows, globals_ = scan(a.project)
    base_flows, base_globals = scan(a.base) if a.base else ({}, {})

    new_flows = {n: v for n, v in flows.items() if n not in base_flows}
    endpoints = []  # (name, file, resource, operation)
    for name, locs in new_flows.items():
        for rel, el in locs:
            lst = el.find(HTTP + "listener")
            if lst is not None and lst.get("path"):
                seg = [s for s in lst.get("path").split("/") if s]
                resource = seg[0] if seg else ""
                endpoints.append((name, rel, resource, operation_of(lst.get("allowedMethods"), lst.get("path"))))

    res = {}
    if not endpoints:
        res["F1"] = ("FAIL", f"no new endpoint flow; new flows={sorted(new_flows)}")
        res["F2"] = ("FAIL", "no new endpoint flow")
    else:
        f1 = [(n, fill(naming["flow"], r, o)) for n, _, r, o in endpoints]
        f2 = [(n, f, fill(naming["implFile"], r, o)) for n, f, r, o in endpoints]
        res["F1"] = ("PASS" if all(n == w for n, w in f1) else "FAIL",
                     "; ".join(f"{n} (want {w})" for n, w in f1))
        res["F2"] = ("PASS" if all(f == w for _, f, w in f2) else "FAIL",
                     "; ".join(f"{n} in {f} (want {w})" for n, f, w in f2))

    want_global = naming["globalConfigFile"]
    new_globals = {k: v for k, v in globals_.items() if k not in base_globals}
    if not new_globals:
        res["F3"] = ("N/A", "no new global element")
    else:
        bad = {f"{t}:{n}": v for (t, n), v in new_globals.items() if v != [want_global]}
        res["F3"] = ("FAIL" if bad else "PASS",
                     f"want {want_global}; new={ {f'{t}:{n}': v for (t, n), v in new_globals.items()} }")

    var_re = variable_regex(naming["variable"])
    new_vars = sorted({v for locs in new_flows.values() for _, el in locs for v in variables_in(el)})
    if not new_vars:
        res["F4"] = ("N/A", "no new flow variable")
    else:
        bad = [v for v in new_vars if not var_re.match(v)]
        res["F4"] = ("FAIL" if bad else "PASS", f"rule {naming['variable']!r}; vars={new_vars}; bad={bad}")

    for k, (v, why) in res.items():
        print(f"{k} {v}: {why}")
    if a.base:
        gone_flows = sorted(set(base_flows) - set(flows))
        moved = sorted(n for n in base_flows if n in flows and [r for r, _ in flows[n]] != [r for r, _ in base_flows[n]])
        print(f"INFO legacy: flows gone={gone_flows} flows moved={moved}")
    ok = all(v in ("PASS", "N/A") for v, _ in res.values())
    print("VERDICT", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

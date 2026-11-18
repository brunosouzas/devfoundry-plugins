#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""T8 grader (grading.md). Usage: uv run grade.py <project dir> <run.jsonl>"""
import json, subprocess, sys, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET

here = Path(__file__).resolve().parent
evals = here.parent.parent
resolver = evals.parent.parent / "plugins/engineering-profile/skills/project-profile/scripts/resolve-profile.py"
project, run = Path(sys.argv[1]), Path(sys.argv[2])
CORE = "{http://www.mulesoft.org/schema/mule/core}"

def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in (root / "engineering").rglob("*") if p.is_file()}
untouched = tree(project) == tree(here / "fixture")
print(f"L0 {'PASS' if untouched else 'FAIL'}: engineering/ (profile and pack) unchanged by the run")
eff = subprocess.run([sys.executable, str(resolver), str(here / "fixture"), "--emit-profile"], capture_output=True, text=True, check=True).stdout
with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
    f.write(eff)
l1 = subprocess.run([sys.executable, str(evals / "cases/T3/check.py"), str(project), f.name, "--base", str(here / "fixture")],
                    capture_output=True, text=True)
print(l1.stdout.strip())

base = {el.get("name") for p in (here / "fixture/src/main/mule").rglob("*.xml") for el in ET.parse(p).getroot()}
flows = {el.get("name"): el for p in (project / "src/main/mule").rglob("*.xml") for el in ET.parse(p).getroot()
         if el.tag in (CORE + "flow", CORE + "sub-flow")}

def reached(name, seen):
    """The flow and every flow or sub-flow it reaches with flow-ref."""
    if name in seen or name not in flows:
        return seen
    seen.add(name)
    for ref in flows[name].iter(CORE + "flow-ref"):
        reached(ref.get("name"), seen)
    return seen

loggers = {}
for name, el in flows.items():
    if name not in base and el.find(".//{http://www.mulesoft.org/schema/mule/http}listener") is not None:
        loggers[name] = sum(1 for f in reached(name, set()) for lg in flows[f].iter(CORE + "logger")
                            if lg.get("category") == "com.acme.api.products")
l2 = bool(loggers) and all(n >= 2 for n in loggers.values())
print(f"L2 {'PASS' if l2 else 'FAIL'}: loggers with category com.acme.api.products per new endpoint flow: {loggers}")

answer = ""
for line in run.read_text().splitlines():
    e = json.loads(line)
    if e.get("type") == "result":
        answer = e.get("result") or ""
l3 = "ACME-LOG-1" in answer and "camelCase" in answer
print(f"L3 {'PASS' if l3 else 'FAIL'}: ACME-LOG-1 in answer={'ACME-LOG-1' in answer}, camelCase in answer={'camelCase' in answer}")
ok = untouched and l1.returncode == 0 and l2 and l3
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)

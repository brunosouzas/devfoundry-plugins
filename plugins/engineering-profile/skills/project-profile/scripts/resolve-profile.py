#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Resolve a project's engineering profile and its packs into the rules in effect (profiles/SCHEMA.md).

Usage: resolve-profile.py [project dir] [--rules-root DIR]... [--json] [--emit-profile] [--strict]
  project dir     the project root that holds engineering/profile.yaml (default: .)
  --rules-root    a folder searched for rules.md files with the public rules; repeatable
                  (default: the plugins/ folder this script ships in)
  --json          print the result as JSON instead of the report
  --emit-profile  print only the effective profile (mulesoft section) as YAML, for graders
  --strict        exit 1 when a change was refused (a floor rule), not only on errors

Exit 0 = resolved; 1 = errors (or a refusal with --strict); 2 = usage or missing file.
Run with `uv run resolve-profile.py`, or with any python3 that has PyYAML.
"""
import argparse, json, re, sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("resolve-profile.py needs PyYAML: run it with `uv run resolve-profile.py` or `pip install pyyaml`.")

RULE_LINE = re.compile(r"^- \*\*([A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d+)\*\*(\s*\(floor\))?\s*(.*)$")
NEW_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d+$")
VERSIONS = {"engineering.poc/v0", "devfoundry/v1"}
MULE_SECTIONS = ("naming", "precedence", "components")


def default_rules_root():
    # .../plugins/engineering-profile/skills/project-profile/scripts/resolve-profile.py -> .../plugins
    return Path(__file__).resolve().parents[4]


def public_rules(roots):
    rules = {}
    for root in roots:
        for f in sorted(Path(root).rglob("rules.md")):
            for line in f.read_text().splitlines():
                m = RULE_LINE.match(line)
                if m and m.group(1) not in rules:
                    rules[m.group(1)] = {"text": m.group(3).strip(), "floor": bool(m.group(2)),
                                         "layer": "public", "source": str(f), "status": "active"}
    return rules


def load(path, kind, errors):
    try:
        data = yaml.safe_load(Path(path).read_text()) or {}
    except yaml.YAMLError as e:
        errors.append(f"{path}: not valid YAML ({e})"); return None
    if not isinstance(data, dict):
        errors.append(f"{path}: not a mapping"); return None
    if data.get("apiVersion") not in VERSIONS:
        errors.append(f"{path}: apiVersion must be one of {sorted(VERSIONS)}, got {data.get('apiVersion')!r}")
    if data.get("kind") != kind:
        errors.append(f"{path}: kind must be {kind}, got {data.get('kind')!r}")
    return data


def resolve(project, roots):
    project = Path(project)
    errors, refused, changes, replaced = [], [], [], []
    profile_path = project / "engineering/profile.yaml"
    if not profile_path.is_file():
        return {"errors": [f"{profile_path}: not found"], "missing": True}
    rules = public_rules(roots)
    profile = load(profile_path, "EngineeringProfile", errors)
    if profile is None:
        return {"errors": errors}
    v0 = profile.get("apiVersion") == "engineering.poc/v0"
    if v0 and ("extends" in profile or "rules" in profile):
        errors.append(f"{profile_path}: extends and rules need apiVersion devfoundry/v1")

    layers = []
    for entry in profile.get("extends") or []:
        pack_path = project / str(entry) / "pack.yaml"
        if not pack_path.is_file():
            errors.append(f"extends {entry}: no pack.yaml in that folder"); continue
        pack = load(pack_path, "RulesPack", errors)
        if pack is None:
            continue
        if "extends" in pack:
            errors.append(f"{pack_path}: a pack has no extends; list every pack in the project profile")
        layers.append((f"pack {pack.get('name', entry)}@{pack.get('version', '?')}", pack))
    layers.append(("project", profile))

    mule = {s: {} for s in MULE_SECTIONS}
    origin = {s: {} for s in MULE_SECTIONS}
    for name, data in layers:
        for section in MULE_SECTIONS:
            for key, value in ((data.get("mulesoft") or {}).get(section) or {}).items():
                if key in mule[section] and mule[section][key] != value:
                    replaced.append({"key": f"mulesoft.{section}.{key}", "layer": name, "value": value,
                                     "was": mule[section][key], "was_layer": origin[section][key]})
                mule[section][key] = value; origin[section][key] = name
        r = data.get("rules") or {}
        for item in r.get("add") or []:
            rid = (item or {}).get("id", "")
            if not NEW_ID.match(str(rid)):
                errors.append(f"{name}: add id {rid!r} is not of the form PREFIX-N"); continue
            if rid in rules:
                errors.append(f"{name}: add {rid} exists already ({rules[rid]['layer']}); use override"); continue
            missing = [k for k in ("text", "why", "check") if not item.get(k)]
            if missing:
                errors.append(f"{name}: add {rid} misses {', '.join(missing)}"); continue
            rules[rid] = {"text": item["text"], "floor": False, "layer": name, "source": name, "status": "active"}
            changes.append({"id": rid, "action": "add", "layer": name})
        for rid, spec in (r.get("override") or {}).items():
            text = spec.get("text") if isinstance(spec, dict) else spec
            if rid not in rules:
                errors.append(f"{name}: override {rid}: no such rule"); continue
            if rules[rid]["floor"]:
                refused.append({"id": rid, "action": "override", "layer": name}); continue
            if not text:
                errors.append(f"{name}: override {rid} has no text"); continue
            changes.append({"id": rid, "action": "override", "layer": name, "was_layer": rules[rid]["layer"]})
            rules[rid].update(text=str(text), layer=name, status="active")
        for rid, reason in (r.get("disable") or {}).items():
            if rid not in rules:
                errors.append(f"{name}: disable {rid}: no such rule"); continue
            if rules[rid]["floor"]:
                refused.append({"id": rid, "action": "disable", "layer": name}); continue
            if not reason or not str(reason).strip():
                errors.append(f"{name}: disable {rid} needs a reason"); continue
            changes.append({"id": rid, "action": "disable", "layer": name, "reason": str(reason)})
            rules[rid].update(layer=name, status="disabled")
    return {"layers": [n for n, _ in layers], "mulesoft": mule, "replaced": replaced, "changes": changes,
            "refused": refused, "errors": errors, "rules": rules}


def report(res):
    out = ["Layers (lowest first): public, " + ", ".join(res["layers"])]
    out.append("Rules changed:" if res["changes"] else "Rules changed: none")
    for c in res["changes"]:
        extra = f" (was {c['was_layer']})" if c.get("was_layer") else ""
        extra += f": {c['reason']}" if c.get("reason") else ""
        out.append(f"  {c['id']} {c['action']} by {c['layer']}{extra}")
    for r in res["refused"]:
        out.append(f"REFUSED {r['action']} of floor rule {r['id']} by {r['layer']}: the public rule stays")
    for r in res["replaced"]:
        out.append(f"REPLACED {r['key']}: {r['value']!r} ({r['layer']}) over {r['was']!r} ({r['was_layer']})")
    out.append("Effective mulesoft settings:")
    for section in MULE_SECTIONS:
        for k, v in res["mulesoft"][section].items():
            out.append(f"  {section}.{k}: {v}")
    for e in res["errors"]:
        out.append(f"ERROR {e}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--rules-root", action="append")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--emit-profile", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    res = resolve(a.project, [Path(p) for p in (a.rules_root or [default_rules_root()])])
    if res.get("missing"):
        print(res["errors"][0], file=sys.stderr); return 2
    if a.emit_profile:
        print(yaml.safe_dump({"mulesoft": res.get("mulesoft", {})}, sort_keys=False), end="")
    elif a.json:
        print(json.dumps(res, indent=2))
    else:
        print(report(res) if "layers" in res else "\n".join(f"ERROR {e}" for e in res["errors"]))
    if res["errors"] or (a.strict and res.get("refused")):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

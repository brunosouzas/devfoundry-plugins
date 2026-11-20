#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Resolve a project's engineering profile and its packs into the rules in effect.

The merge rules are in ../references/layers.md. Usage:
  resolve-profile.py [project dir] [--rules-root DIR]... [--json] [--emit-profile] [--strict]
  project dir     the project root that holds engineering/profile.yaml (default: .)
  --rules-root    a folder searched for rules.md files with the public rules; repeatable. Default: every mulesmith
                  plugin next to this one (the repository's plugins/ folder, or the latest installed version of each
                  plugin of the same marketplace)
  --json          print the result as JSON instead of the report
  --emit-profile  print only the effective mulesoft settings as YAML (nothing when there are errors)
  --strict        exit 1 when a change was refused (a floor rule), not only on errors

Exit 0 = resolved; 1 = errors (or a refusal with --strict); 2 = usage or missing profile.
Run with `uv run resolve-profile.py`, or with any python3 that has PyYAML.
"""
import argparse, json, re, sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("resolve-profile.py needs PyYAML: run it with `uv run resolve-profile.py` or `pip install pyyaml`.")

ID = r"[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d+"
RULE_LINE = re.compile(rf"^- \*\*({ID})\*\*(\s*\(floor\))?\s*(.*)$")
NEW_ID = re.compile(rf"^{ID}$")
CLASSES = ("auto", "propose", "ask")
CLASS_LINE = re.compile(r"^\s+Class:\s*`?(\w+)`?\s*$")
DEFAULT_CLASS = "auto"
VERSIONS = {"engineering.poc/v0", "mulesmith/v1"}
MULE_SECTIONS = ("naming", "precedence", "components")


def prefix(rule_id):
    return rule_id.rsplit("-", 1)[0]


def default_rules_roots(script=None):
    """The plugin folders whose rules.md files hold the public rules.

    Repository or --plugin-dir layout: <plugins>/<plugin>/skills/... -> every <plugin> under <plugins>.
    Installed layout: <cache>/<marketplace>/<plugin>/<version>/skills/... -> the latest <version> of each <plugin>.
    """
    plugin_root = Path(script or __file__).resolve().parents[3]
    parent = plugin_root.parent
    try:
        name = json.loads((plugin_root / ".claude-plugin/plugin.json").read_text()).get("name")
    except (OSError, ValueError):
        name = None
    if plugin_root.name == name or parent.name == "plugins":  # the folder is named after the plugin: not a version
        return sorted(d for d in parent.iterdir() if (d / ".claude-plugin/plugin.json").is_file())
    roots = []
    for plugin in sorted(d for d in parent.parent.iterdir() if d.is_dir()):
        versions = [v for v in plugin.iterdir() if (v / ".claude-plugin/plugin.json").is_file()]
        if versions:
            roots.append(max(versions, key=lambda v: v.stat().st_mtime))
    return roots or [plugin_root]


def public_rules(roots, errors=None):
    """The rules of every rules.md under roots. A rule's block is its line and the indented lines right after it;
    its `Class:` line must be in that block. A rule without one is `auto`; an unknown or repeated class is an error."""
    rules = {}
    errors = [] if errors is None else errors
    for root in roots:
        for f in sorted(Path(root).rglob("rules.md")):
            current = None
            for line in f.read_text().splitlines():
                m = RULE_LINE.match(line)
                if m:
                    current = None
                    if m.group(1) not in rules:
                        current = m.group(1)
                        rules[current] = {"text": m.group(3).strip(), "floor": bool(m.group(2)), "class": DEFAULT_CLASS,
                                          "class_declared": False, "layer": "public", "source": str(f), "status": "active"}
                    continue
                if not line.startswith((" ", "\t")):  # a blank line, a heading or another paragraph ends the block
                    current = None; continue
                c = CLASS_LINE.match(line)
                if c and current:
                    rule = rules[current]
                    if c.group(1) not in CLASSES:
                        errors.append(f"{f}: {current}: Class must be one of {', '.join(CLASSES)}, got {c.group(1)!r}")
                    elif rule["class_declared"]:
                        errors.append(f"{f}: {current}: more than one Class line")
                    else:
                        rule.update({"class": c.group(1), "class_declared": True})
    return rules


def load(path, kind, errors):
    try:
        data = yaml.safe_load(Path(path).read_text()) or {}
    except yaml.YAMLError as e:
        errors.append(f"{path}: not valid YAML ({e})"); return None
    if not isinstance(data, dict):
        errors.append(f"{path}: not a mapping"); return None
    bad = False
    if data.get("apiVersion") not in VERSIONS:
        errors.append(f"{path}: apiVersion must be one of {sorted(VERSIONS)}, got {data.get('apiVersion')!r}"); bad = True
    if data.get("kind") != kind:
        errors.append(f"{path}: kind must be {kind}, got {data.get('kind')!r}"); bad = True
    return None if bad else data


def mapping(value, where, errors):
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"{where} must be a mapping, got {type(value).__name__}"); return {}
    return value


def check_layer_shape(name, data, errors):
    """Type-check one layer; return (mulesoft sections, add list, override map, disable map)."""
    mule = mapping(data.get("mulesoft"), f"{name}: mulesoft", errors)
    sections = {s: mapping(mule.get(s), f"{name}: mulesoft.{s}", errors) for s in MULE_SECTIONS}
    rules = mapping(data.get("rules"), f"{name}: rules", errors)
    add = rules.get("add") or []
    if not isinstance(add, list):
        errors.append(f"{name}: rules.add must be a list of rules"); add = []
    override = mapping(rules.get("override"), f"{name}: rules.override", errors)
    disable = mapping(rules.get("disable"), f"{name}: rules.disable", errors)
    seen = {}
    for action, ids in (("add", [i.get("id") for i in add if isinstance(i, dict)]), ("override", override), ("disable", disable)):
        for rid in ids:
            seen.setdefault(rid, []).append(action)
    for rid, actions in seen.items():
        if len(actions) > 1:
            errors.append(f"{name}: {rid} appears in {' and '.join(actions)}; one change per rule per layer")
    return sections, add, override, disable


def resolve(project, roots):
    project = Path(project).resolve()
    errors, refused, changes, replaced = [], [], [], []
    profile_path = project / "engineering/profile.yaml"
    if not profile_path.is_file():
        return {"errors": [f"{profile_path}: not found"], "missing": True}
    rules = public_rules(roots, errors)
    public_prefixes = {prefix(r) for r in rules}
    profile = load(profile_path, "EngineeringProfile", errors)
    if profile is None:
        return {"errors": errors}
    if profile.get("apiVersion") == "engineering.poc/v0" and ("extends" in profile or "rules" in profile):
        errors.append(f"{profile_path}: extends and rules need apiVersion mulesmith/v1")

    layers, seen_packs = [], set()
    extends = profile.get("extends") or []
    if not isinstance(extends, list):
        errors.append("extends must be a list of pack folders"); extends = []
    for entry in extends:
        folder = (project / str(entry)).resolve()
        if project not in folder.parents:
            errors.append(f"extends {entry}: a pack folder must be inside the project (engineering/packs/<name>)"); continue
        if folder in seen_packs:
            errors.append(f"extends {entry}: listed twice"); continue
        seen_packs.add(folder)
        pack_path = folder / "pack.yaml"
        if not pack_path.is_file():
            errors.append(f"extends {entry}: no pack.yaml in that folder"); continue
        pack = load(pack_path, "RulesPack", errors)
        if pack is None:
            continue
        if "extends" in pack:
            errors.append(f"{pack_path}: a pack has no extends; list every pack in the project profile")
        if not pack.get("name") or not pack.get("version"):
            errors.append(f"{pack_path}: a pack needs a name and a version")
        layers.append((f"pack {pack.get('name', entry)}@{pack.get('version', '?')}", pack))
    layers.append(("project", profile))

    mule = {s: {} for s in MULE_SECTIONS}
    origin = {s: {} for s in MULE_SECTIONS}
    for name, data in layers:
        sections, add, override, disable = check_layer_shape(name, data, errors)
        for section in MULE_SECTIONS:
            for key, value in sections[section].items():
                if key in mule[section] and mule[section][key] != value:
                    replaced.append({"key": f"mulesoft.{section}.{key}", "layer": name, "value": value,
                                     "was": mule[section][key], "was_layer": origin[section][key]})
                mule[section][key] = value; origin[section][key] = name
        for item in add:
            if not isinstance(item, dict):
                errors.append(f"{name}: each rules.add item is a mapping with id, text, why and check"); continue
            rid = str(item.get("id", ""))
            if not NEW_ID.match(rid):
                errors.append(f"{name}: add id {rid!r} is not of the form PREFIX-N"); continue
            if rid in rules:
                errors.append(f"{name}: add {rid} exists already ({rules[rid]['layer']}); use override"); continue
            if prefix(rid) in public_prefixes:
                errors.append(f"{name}: add {rid} uses the public prefix {prefix(rid)}; use a prefix of your own"); continue
            missing = [k for k in ("text", "why", "check") if not isinstance(item.get(k), str) or not item[k].strip()]
            if missing:
                errors.append(f"{name}: add {rid} misses {', '.join(missing)}"); continue
            cls = item.get("class") if item.get("class") is not None else DEFAULT_CLASS
            if cls not in CLASSES:
                errors.append(f"{name}: add {rid}: class must be one of {', '.join(CLASSES)}, got {cls!r}"); continue
            rules[rid] = {"text": item["text"], "floor": False, "class": cls, "layer": name, "source": name, "status": "active"}
            changes.append({"id": rid, "action": "add", "layer": name})
        for rid, spec in override.items():
            text = spec.get("text") if isinstance(spec, dict) else spec
            cls = spec.get("class") if isinstance(spec, dict) else None
            if rid not in rules:
                errors.append(f"{name}: override {rid}: no such rule"); continue
            if rules[rid]["floor"]:
                refused.append({"id": rid, "action": "override", "layer": name}); continue
            if cls is not None and cls not in CLASSES:
                errors.append(f"{name}: override {rid}: class must be one of {', '.join(CLASSES)}, got {cls!r}"); continue
            if text is None and cls is not None:
                text = rules[rid]["text"]
            elif not isinstance(text, str) or not text.strip():
                errors.append(f"{name}: override {rid} needs the rule's text or class (a string, or a mapping with text, class or both)"); continue
            rule = rules[rid]
            if rule["status"] == "active" and text == rule["text"] and cls in (None, rule["class"]):
                continue  # the layer restates the rule as it is: nothing changes, nothing to report
            change = {"id": rid, "action": "override", "layer": name, "was_layer": rule["layer"]}
            if cls is not None and cls != rule["class"]:
                change.update({"class": cls, "was_class": rule["class"]})
            if rule["status"] == "disabled":
                change["enabled_again"] = True
            changes.append(change)
            rules[rid].update(text=text, layer=name, status="active", **({"class": cls} if cls else {}))
        for rid, reason in disable.items():
            if rid not in rules:
                errors.append(f"{name}: disable {rid}: no such rule"); continue
            if rules[rid]["floor"]:
                refused.append({"id": rid, "action": "disable", "layer": name}); continue
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{name}: disable {rid} needs a reason (a string)"); continue
            changes.append({"id": rid, "action": "disable", "layer": name, "reason": reason})
            rules[rid].update(layer=name, status="disabled")
    return {"layers": [n for n, _ in layers], "mulesoft": mule, "replaced": replaced, "changes": changes,
            "refused": refused, "errors": errors, "rules": rules}


def report(res):
    out = ["Layers (lowest first): public, " + ", ".join(res["layers"])]
    out.append("Rules changed:" if res["changes"] else "Rules changed: none")
    for c in res["changes"]:
        extra = f" (was {c['was_layer']})" if c.get("was_layer") else ""
        extra += f", class {c['was_class']} -> {c['class']}" if c.get("was_class") else ""
        extra += ", enabled again" if c.get("enabled_again") else ""
        extra += f": {c['reason']}" if c.get("reason") else ""
        out.append(f"  {c['id']} {c['action']} by {c['layer']}{extra}")
    for r in res["refused"]:
        out.append(f"REFUSED {r['action']} of floor rule {r['id']} by {r['layer']}: the public rule stays")
    for r in res["replaced"]:
        out.append(f"REPLACED {r['key']}: {r['value']!r} ({r['layer']}) over {r['was']!r} ({r['was_layer']})")
    if "rules" in res:
        for cls in ("ask", "propose"):
            ids = sorted(rid for rid, r in res["rules"].items() if r["status"] == "active" and r["class"] == cls)
            out.append(f"Rules of class {cls}: " + (", ".join(ids) if ids else "none"))
    out.append("Effective mulesoft settings:")
    for section in MULE_SECTIONS:
        for k, v in res["mulesoft"][section].items():
            out.append(f"  {section}.{k}: {v}")
    for e in res["errors"]:
        out.append(f"ERROR {e}")
    if res["errors"]:
        out.append("The profile has errors: fix them before the rules above are used.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--rules-root", action="append")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--emit-profile", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    res = resolve(a.project, [Path(p) for p in a.rules_root] if a.rules_root else default_rules_roots())
    if res.get("missing"):
        print(res["errors"][0], file=sys.stderr); return 2
    if a.emit_profile:
        if res["errors"]:
            print("\n".join(f"ERROR {e}" for e in res["errors"]), file=sys.stderr)
        else:
            print(yaml.safe_dump({"mulesoft": res["mulesoft"]}, sort_keys=False), end="")
    elif a.json:
        print(json.dumps(res, indent=2))
    else:
        print(report(res) if "layers" in res else "\n".join(f"ERROR {e}" for e in res["errors"]))
    if res["errors"] or (a.strict and res.get("refused")):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

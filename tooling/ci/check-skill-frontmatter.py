"""Parse the frontmatter of every SKILL.md with a strict YAML parser.

Claude Code's loader tolerates a plain `description:` that contains ": ", but strict
YAML (PyYAML, GitHub's renderer, other hosts) rejects it. Quote such values.
Usage: python3 check-skill-frontmatter.py [repo root]
"""
import pathlib
import re
import sys

import yaml

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
failed = 0
for path in sorted(root.glob("plugins/*/skills/*/SKILL.md")):
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\n(.*?)\n---[ \t]*(\n|\Z)", text, re.S)
    if not match:
        print(f"FAIL {path}: no frontmatter")
        failed += 1
        continue
    try:
        data = yaml.safe_load(match.group(1))
        if not isinstance(data, dict) or not data.get("name") or not isinstance(data.get("description"), str):
            raise ValueError("name and description are required")
    except Exception as exc:  # noqa: BLE001 - report every file
        print(f"FAIL {path}: {str(exc).splitlines()[0]}")
        failed += 1
    else:
        print(f"ok   {path}")
sys.exit(1 if failed else 0)

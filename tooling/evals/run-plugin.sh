#!/usr/bin/env bash
# Plugin arm for one fixed case: run-baseline.sh plus only the plugins under test.
# Three flag changes against the baseline (see README.md, "Plugin arm"). MODEL is required.
# Usage: MODEL=<model id> run-plugin-v2.sh <case: T1b|T2|T5|T6|T3bA|T3bB> <run number> <work root> <results dir> <plugin dir>...
# One --plugin-dir (and --add-dir, so the skills can read their references) per plugin dir given.
set -euo pipefail
case_id="$1"; n="$2"; work="$3"; results="$4"; shift 4; model="${MODEL:?set MODEL}"
plugin_args=(); for p in "$@"; do d="$(cd "$p" && pwd)"; plugin_args+=(--plugin-dir "$d" --add-dir "$d"); done
here="$(cd "$(dirname "$0")" && pwd)"
case "$case_id" in
  T1b) t=T1b; profile="";;
  T2) t=T2; profile="";;
  T5) t=T5; profile="";;
  T6) t=T6; profile="";;
  T3bA) t=T3b; profile=profile-a.yaml;;
  T3bB) t=T3b; profile=profile-b.yaml;;
  *) echo "unknown case $case_id" >&2; exit 2;;
esac
id="$case_id-r$n"
dir="$work/$model/$id/project"
rm -rf "$work/$model/$id"; mkdir -p "$dir" "$results"
cp -R "$here/cases/$t/fixture/." "$dir/"
if [ -n "$profile" ]; then mkdir -p "$dir/engineering"; cp "$here/../../profiles/examples/$profile" "$dir/engineering/profile.yaml"; fi
prompt="${PROMPT:-$(cat "$here/cases/$t/prompt.md")}"  # PROMPT override: harness smoke check only
settings="$(cat "$here/plugin-arm-settings.json")"
(cd "$dir" && claude -p "$prompt" \
  --model "$model" \
  --setting-sources project \
  --strict-mcp-config \
  --settings "$settings" \
  "${plugin_args[@]}" \
  --permission-mode acceptEdits \
  --add-dir "$dir" \
  --output-format stream-json --verbose > "$results/$id.jsonl" 2> "$results/$id.stderr") || true
mkdir -p "$results/$id.files"
cp -R "$dir/." "$results/$id.files/"
diff -ruN "$here/cases/$t/fixture" "$dir" -x engineering > "$results/$id.diff" || true
echo "done $model $id"

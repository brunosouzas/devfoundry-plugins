#!/usr/bin/env bash
# Baseline arm (no plugin) for one fixed case. Runs outside the repository, in a temp copy of the fixture; MODEL is required.
# Isolation flags: see README.md. Verify with verify-init.py.
# Usage: MODEL=<model id> run-baseline-v2.sh <case: T1b|T2|T5|T6|T3bA|T3bB> <run number> <work root> <results dir>
set -euo pipefail
case_id="$1"; n="$2"; work="$3"; results="$4"; model="${MODEL:?set MODEL}"
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
(cd "$dir" && claude -p "$prompt" \
  --model "$model" \
  --setting-sources project \
  --strict-mcp-config \
  --disable-slash-commands \
  --permission-mode acceptEdits \
  --add-dir "$dir" \
  --output-format stream-json --verbose > "$results/$id.jsonl" 2> "$results/$id.stderr") || true
mkdir -p "$results/$id.files"
cp -R "$dir/." "$results/$id.files/"
diff -ruN "$here/cases/$t/fixture" "$dir" -x engineering > "$results/$id.diff" || true
echo "done $model $id"

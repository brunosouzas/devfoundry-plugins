#!/usr/bin/env bash
# Plugin arm for one fixed case: run-baseline.sh plus only the plugins under test.
# Three flag changes against the baseline (see README.md, "Plugin arm"). MODEL is required.
# Usage: MODEL=<model id> run-plugin-v2.sh <case: T1b|T2|T5|T6|T3bA|T3bB|T8|T9|TAPI> <run number> <work root> <results dir> <plugin dir>...
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
  T8) t=T8; profile="";;
  T9) t=T9; profile="";;
  TAPI) t=TAPI; profile="";;  # the full-API benchmark; its fixture carries its own engineering/profile.yaml
  T3bA) t=T3b; profile=profile-a.yaml;;
  T3bB) t=T3b; profile=profile-b.yaml;;
  *) echo "unknown case $case_id" >&2; exit 2;;
esac
# The full-API benchmark builds and tests its project: mvn is pre-approved (a pre-approval, not a limit; see README.md).
extra=(); [ "$t" = TAPI ] && extra=(--allowedTools "Bash(mvn:*)")
if [ "$t" = TAPI ]; then  # Maven 3.9 and Java 17 first on PATH: 3.10 breaks the Mule plugins (README, Requirements)
  mvn39="${MVN:-$HOME/.local/share/mise/installs/maven/3.9.15/apache-maven-3.9.15/bin/mvn}"
  export JAVA_HOME="${JAVA17_HOME:-$HOME/.local/share/mise/installs/java/temurin-17.0.21+9}"
  export PATH="$(dirname "$mvn39"):$JAVA_HOME/bin:$PATH"
fi
id="$case_id-r$n"
dir="$work/$model/$id/project"
rm -rf "$work/$model/$id"; mkdir -p "$dir" "$results"
cp -R "$here/cases/$t/fixture/." "$dir/"
if [ -n "$profile" ]; then mkdir -p "$dir/engineering"; cp "$here/../../examples/profiles/$profile" "$dir/engineering/profile.yaml"; fi
prompt="${PROMPT:-$(cat "$here/cases/$t/prompt.md")}"  # PROMPT override: harness smoke check only
settings="$(cat "$here/plugin-arm-settings.json")"
(cd "$dir" && claude -p "$prompt" \
  --model "$model" \
  --setting-sources project \
  --strict-mcp-config \
  --settings "$settings" \
  "${plugin_args[@]}" \
  --permission-mode acceptEdits \
  ${extra[@]+"${extra[@]}"} \
  --add-dir "$dir" \
  --output-format stream-json --verbose > "$results/$id.jsonl" 2> "$results/$id.stderr") || true
mkdir -p "$results/$id.files"
cp -R "$dir/." "$results/$id.files/"
diff -ruN "$here/cases/$t/fixture" "$dir" -x engineering > "$results/$id.diff" || true
echo "done $model $id"

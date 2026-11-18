#!/usr/bin/env bash
# T4/T7 (H3): build each project a run left (case T1b by default, CASE=T5 for T7) exactly as it is and run its MUnit tests.
# Usage: run-build.sh <scratch dir> <runs dir> <out dir>  (CASE=T1b by default, CASE=T5 for the circuit breaker)
# Toolchain: Java 17 and Maven 3.9.x. JAVA17_HOME and MVN override the defaults below (mise paths on the maintainer's Mac).
# The MuleSoft EE repository credential comes from the user's ~/.m2/settings.xml; nothing is written here.
# Prints, per project: the mvn exit code, the MUnit totals and each test that did not pass.
# PASS = exit 0 (build ok and every test green) and the project has the pattern's test (T4: duplicate; T7: open circuit), checked by the grader.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; scratch="$1"
runs="${2:?runs dir}"; out="${3:?out dir}"; mkdir -p "$out"; c="${CASE:-T1b}"
export JAVA_HOME="${JAVA17_HOME:-$HOME/.local/share/mise/installs/java/temurin-17.0.21+9}"
mvn="${MVN:-$HOME/.local/share/mise/installs/maven/3.9.15/apache-maven-3.9.15/bin/mvn}"
for m in claude-opus-5-5 claude-sonnet-5-5; do for n in 1 2 3; do
  src="$runs/$m/$c-r$n.files"
  [ -d "$src" ] || continue
  if [ ! -s "$runs/$m/$c-r$n.diff" ]; then echo "$m $c-r$n: empty diff, no code, skipped"; continue; fi
  dir="$scratch/$m/$c-r$n"; rm -rf "$dir"; mkdir -p "$dir"; cp -R "$src/." "$dir/"
  log="$out/${m}_$c-r$n.log"
  (cd "$dir" && "$mvn" -B clean test) > "$log" 2>&1; rc=$?
  echo "$m $c-r$n: exit=$rc $(grep -E '^= Tests run' "$log" | tail -1) $(grep -oE -- '--- [A-Za-z0-9_-]+ <<< [A-Z]+' "$log" | tr '\n' ';')"
  [ $rc -eq 0 ] || grep -m1 -oE 'Failed to execute goal .{0,250}' "$log" | grep -v 'MUnit Tests Failed' | sed 's/^/    /'
done; done

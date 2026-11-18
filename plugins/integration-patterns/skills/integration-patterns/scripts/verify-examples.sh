#!/usr/bin/env bash
# Builds every verified example in assets/<platform>/<pattern>/ and runs its tests, so the examples the
# references point to are known to compile and pass. Each project is copied to a temp dir first, so the skill
# folder stays clean.
# Mule 4 examples need Maven 3.9.x (3.10.0 breaks mule-maven-plugin), a Java 17 JAVA_HOME and access to the
# MuleSoft EE repository.
# Usage: verify-examples.sh [log dir]. MVN overrides the maven binary. Exit 0 = every example builds and passes.
set -uo pipefail
skill_dir="$(cd "$(dirname "$0")/.." && pwd)"
mvn="${MVN:-mvn}"; logs="${1:-}"; rc=0
for example in "$skill_dir"/assets/*/*/; do
  example="${example%/}"; name="$(basename "$(dirname "$example")")/$(basename "$example")"
  [ -f "$example/pom.xml" ] || { echo "$name: no pom.xml, skipped"; continue; }
  tmp="$(mktemp -d)"; cp -R "$example/." "$tmp/"
  log="/dev/null"; [ -n "$logs" ] && { mkdir -p "$logs"; log="$logs/${name//\//-}.log"; }
  if (cd "$tmp" && "$mvn" -B clean test) > "$log" 2>&1; then echo "$name: OK"; else echo "$name: FAILED (log: $log)"; rc=1; fi
  rm -rf "${tmp:?}"
done
exit $rc
